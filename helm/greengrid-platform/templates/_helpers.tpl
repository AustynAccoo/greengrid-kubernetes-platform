{{- define "greengrid.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- define "greengrid.fullname" -}}
{{- if .Values.fullnameOverride }}{{ .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}{{ else }}{{ printf "%s-%s" .Release.Name (include "greengrid.name" .) | trunc 63 | trimSuffix "-" }}{{ end }}
{{- end -}}
{{- define "greengrid.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "greengrid.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- with .Values.commonLabels }}
{{ toYaml . }}
{{- end }}
{{- end -}}
{{- define "greengrid.selectorLabels" -}}
app.kubernetes.io/name: {{ include "greengrid.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
{{- define "greengrid.apiName" -}}{{ printf "%s-telemetry-api" (include "greengrid.fullname" .) | trunc 63 | trimSuffix "-" }}{{- end -}}
{{- define "greengrid.generatorName" -}}{{ printf "%s-telemetry-generator" (include "greengrid.fullname" .) | trunc 63 | trimSuffix "-" }}{{- end -}}
{{- define "greengrid.image" -}}
{{- $repository := index . 0 -}}{{- $tag := index . 1 -}}
{{- if or (eq $tag "latest") (not (regexMatch "^git-[0-9a-f]{40}$" $tag)) -}}{{- fail (printf "image tag %q must be git-<40 lowercase hex SHA>" $tag) -}}{{- end -}}
{{- printf "%s:%s" $repository $tag -}}
{{- end -}}
{{- define "greengrid.generatorHealthCommand" -}}{{ printf "import os,time; path=%q; assert time.time()-os.path.getmtime(path) < %v" .Values.telemetryGenerator.probes.healthFile .Values.telemetryGenerator.probes.maximumAgeSeconds }}{{- end -}}

