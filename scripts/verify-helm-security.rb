#!/usr/bin/env ruby
# frozen_string_literal: true

require "yaml"
abort "usage: verify-helm-security.rb <manifest>" unless ARGV.length == 1
documents = YAML.load_stream(File.read(ARGV.fetch(0))).compact
by_kind = documents.group_by { |document| document["kind"] }
required = {"Deployment" => 2, "ServiceAccount" => 2, "ConfigMap" => 2, "Service" => 1,
            "HorizontalPodAutoscaler" => 1, "PodDisruptionBudget" => 1,
            "ResourceQuota" => 1, "LimitRange" => 1, "NetworkPolicy" => 4}
required.each do |kind, minimum|
  actual = by_kind.fetch(kind, []).length
  abort "expected #{minimum}+ #{kind}, found #{actual}" if actual < minimum
end
by_kind.fetch("ServiceAccount").each do |account|
  abort "ServiceAccount token automount must be false" unless account["automountServiceAccountToken"] == false
end
by_kind.fetch("Deployment").each do |deployment|
  name = deployment.dig("metadata", "name")
  pod = deployment.dig("spec", "template", "spec")
  account = pod["serviceAccountName"]
  abort "#{name}: default ServiceAccount" if account.nil? || account == "default"
  abort "#{name}: token automount enabled" unless pod["automountServiceAccountToken"] == false
  %w[hostNetwork hostPID hostIPC].each { |field| abort "#{name}: #{field}" unless pod[field] == false }
  abort "#{name}: hostPath found" if pod.fetch("volumes", []).any? { |volume| volume.key?("hostPath") }
  security = pod.fetch("securityContext")
  abort "#{name}: runAsNonRoot missing" unless security["runAsNonRoot"] == true
  abort "#{name}: RuntimeDefault missing" unless security.dig("seccompProfile", "type") == "RuntimeDefault"
  pod.fetch("containers").each do |container|
    identity = "#{name}/#{container['name']}"
    abort "#{identity}: mutable image" unless container.fetch("image").match?(/:git-[0-9a-f]{40}\z/)
    context = container.fetch("securityContext")
    abort "#{identity}: privileged" unless context["privileged"] == false
    abort "#{identity}: privilege escalation" unless context["allowPrivilegeEscalation"] == false
    abort "#{identity}: writable root" unless context["readOnlyRootFilesystem"] == true
    abort "#{identity}: capabilities" unless context.dig("capabilities", "drop")&.include?("ALL")
    %w[requests limits].each do |type|
      values = container.fetch("resources").fetch(type)
      abort "#{identity}: #{type}" unless values.key?("cpu") && values.key?("memory")
    end
    %w[startupProbe readinessProbe livenessProbe].each do |probe|
      abort "#{identity}: #{probe}" unless container.key?(probe)
    end
  end
end
deny = by_kind.fetch("NetworkPolicy").find do |policy|
  policy.dig("spec", "podSelector") == {} && policy.dig("spec", "policyTypes")&.sort == %w[Egress Ingress]
end
abort "default-deny policy missing" unless deny
puts "Security verification passed for #{ARGV.fetch(0)} (#{documents.length} resources)."
