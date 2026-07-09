{{/*
Expand the name of the chart.
*/}}
{{- define "nethical-recon.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "nethical-recon.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "nethical-recon.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "nethical-recon.labels" -}}
helm.sh/chart: {{ include "nethical-recon.chart" . }}
{{ include "nethical-recon.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "nethical-recon.selectorLabels" -}}
app.kubernetes.io/name: {{ include "nethical-recon.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "nethical-recon.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "nethical-recon.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Database URL
*/}}
{{- define "nethical-recon.databaseUrl" -}}
{{- if .Values.externalDatabase.enabled }}
postgresql://{{ .Values.externalDatabase.user }}:{{ .Values.externalDatabase.password }}@{{ .Values.externalDatabase.host }}:{{ .Values.externalDatabase.port }}/{{ .Values.externalDatabase.database }}
{{- else }}
postgresql://{{ .Values.postgresql.auth.username }}:{{ .Values.postgresql.auth.password }}@{{ include "nethical-recon.fullname" . }}-postgresql:{{ .Values.postgresql.service.port }}/{{ .Values.postgresql.auth.database }}
{{- end }}
{{- end }}

{{/*
Redis URL
*/}}
{{- define "nethical-recon.redisUrl" -}}
{{- if .Values.externalRedis.enabled }}
redis://{{ .Values.externalRedis.host }}:{{ .Values.externalRedis.port }}
{{- else }}
redis://{{ include "nethical-recon.fullname" . }}-redis-master:6379
{{- end }}
{{- end }}

{{/*
Image name
*/}}
{{- define "nethical-recon.image" -}}
{{- if .Values.global.imageRegistry }}
{{- printf "%s/%s:%s" .Values.global.imageRegistry .Values.image.repository (.Values.image.tag | default .Chart.AppVersion) }}
{{- else }}
{{- printf "%s:%s" .Values.image.repository (.Values.image.tag | default .Chart.AppVersion) }}
{{- end }}
{{- end }}
