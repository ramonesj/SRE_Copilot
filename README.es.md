<!-- Navegación de Idioma -->
<div align="right">
  <a href="./README.md">English</a> | <strong>Español</strong>
</div>

<!-- Sección Hero -->
<div align="center">

# SRE Copilot
## Remedio Autónomo de Incidentes con Gobernanza Humana

**IA diagnostica. Humanos autorizan. Automatización remedia. La recuperación se verifica.**

![SRE Copilot Hero](docs/assets/branding/sre-copilot-hero.png)

<!-- Insignias -->
<p align="center">
  <img src="https://img.shields.io/badge/AWS-Cloud-FF9900?logo=amazonaws&logoColor=white" alt="AWS Cloud" />
  <img src="https://img.shields.io/badge/Amazon-Bedrock-232F3E?logo=amazonaws&logoColor=white" alt="Amazon Bedrock" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" alt="Python 3.11+" />
  <img src="https://img.shields.io/badge/Infrastructure_as_Code-CloudFormation-FF9900?logo=amazonaws&logoColor=white" alt="Infrastructure as Code" />
  <img src="https://img.shields.io/badge/Human_in_the_Loop-Required-FF6B6B?logo=people&logoColor=white" alt="Human-in-the-Loop" />
  <img src="https://img.shields.io/badge/Status-MVP_Development-4CAF50?logo=git&logoColor=white" alt="MVP Development Status" />
</p>

</div>

---

## Resumen Ejecutivo

SRE Copilot es una plataforma AIOps/SRE diseñada para aumentar las capacidades de los operadores humanos con análisis impulsado por IA, manteniendo la autoridad humana sobre los cambios en producción. El sistema sigue un flujo de trabajo estricto que garantiza seguridad, responsabilidad y recuperación verificable.

### Flujo de Trabajo Principal:
1. **Detectar** anomalías operativas mediante AWS EventBridge
2. **Crear** incidentes estructurados con evidencia técnica
3. **Recopilar** registros y telemetría completos
4. **Diagnosticar** causas raíz utilizando Amazon Bedrock (LLM)
5. **Evaluar** riesgo de remediación e impacto operativo
6. **Pausar** flujo de trabajo para autorización humana (HITL)
7. **Ejecutar** remediaciones aprobadas mediante AWS Systems Manager
8. **Verificar** recuperación del servicio de manera independiente
9. **Registrar** ciclo de vida completo en traza de auditoría inmutable

## El Problema

La respuesta tradicional a incidentes en entornos de nube requiere que los equipos SRE correlacionen manualmente múltiples fuentes de datos:
- Alertas en tiempo real de sistemas de monitoreo
- Registros de aplicaciones y sistemas
- Telemetría y métricas de infraestructura
- Dependencias de servicio y topología
- Causas raíz probables y opciones de remediación
- Evaluación de riesgo operativo y radio de explosión
- Resultados de ejecución y manejo de errores
- Verificación de salud post-remediación

Este proceso manual es:
- **Lento**: Horas dedicadas a identificar causas raíz durante incidentes críticos
- **Propenso a errores**: El análisis manual puede pasar por alto patrones sutiles o dependencias
- **Inconsistente**: Diferentes operadores responden de manera diferente a incidentes similares
- **No escalable**: A medida que crece la infraestructura en la nube, la respuesta manual se vuelve insostenible
- **Agotador**: La carga cognitiva conduce al agotamiento de operadores y disminución de la efectividad

SRE Copilot reduce esta carga cognitiva y operativa mientras preserva la autoridad humana sobre todas las acciones que cambian el estado.

## Invariante de Seguridad Arquitectónica

<div align="center">
<h3>IA recomienda.<br>Política evalúa.<br>Humano autoriza.<br>Automatización ejecuta.<br>Sistema verifica.<br>Auditoría registra.</h3>
</div>

### Límites de Seguridad Críticos:

1. **El Motor de Diagnóstico de IA NO DEBE modificar infraestructura o invocar remediación directamente**
   - Acceso a Bedrock solo mediante roles IAM (sin almacenamiento de secretos)
   - Permisos de solo lectura para recopilación de evidencia
   - Cero permisos de ejecución para operaciones que cambian el estado

2. **El Motor de Riesgo/Política NO DEBE ejecutar remediación**
   - La evaluación de riesgo es solo recopilación de información de lectura
   - La ejecución es manejada por un componente separado y autorizado

3. **Cada operación que cambia el estado DEBE requerir aprobación explícita de Humano-en-el-Lazo**
   - Sin excepciones independientemente del nivel de riesgo o puntuación de confianza
   - Canales de aprobación configurables (Email/Slack/Teams)
   - Auto-rechazo basado en tiempo de espera después de período configurable

4. **Solo el Motor de Ejecución autorizado puede ejecutar una remediación previamente aprobada**
   - Rol IAM separado con permisos de mínimo privilegio
   - Tokens de ejecución encriptados y nunca registrados
   - Runbooks SSM idempotentes diseñados para ejecución repetida segura

5. **La recuperación debe ser verificada independientemente antes de la resolución del incidente**
   - Éxito de ejecución SSM ≠ recuperación de servicio verificada
   - La verificación de salud utiliza el mismo monitoreo que la detección original
   - Solo la recuperación verificada conduce al estado RESUELTO

## Características Principales

### 🚨 **Detección Automática de Incidentes**
- Integración con EventBridge para Alarmas de CloudWatch y eventos personalizados
- Validación de esquema y deduplicación
- Creación automática de incidentes con identificadores únicos

### 🔍 **Análisis de Causa Raíz Asistido por IA**
- Integración con Amazon Bedrock para análisis de registros y reconocimiento de patrones
- Puntuación de confianza para recomendaciones de diagnóstico
- Identificación de causa raíz basada en evidencia

### ⚖️ **Soporte de Decisiones Consciente del Riesgo**
- Evaluación de impacto operativo
- Cálculo de radio de explosión
- Identificación de Runbooks SSM y verificación de compatibilidad

### 👥 **Aprobación de Humano-en-el-Lazo**
- Canales de aprobación configurables (Email/Slack/Teams)
- Patrón de devolución de llamada de Token de Tarea para reanudación segura del flujo de trabajo
- Gestión de tiempo de espera con auto-rechazo

### ⚡ **Ejecución de Automatización Segura**
- Runbooks SSM idempotentes para remediación a nivel de servicio
- Seguimiento de estado de ejecución y manejo de errores
- Gestión segura de tokens (nunca registrados)

### ✅ **Verificación Independiente de Recuperación**
- Comprobaciones de salud post-ejecución
- Misma fuente de monitoreo que la detección original
- Fallo de verificación activa estado de recuperación fallida

### 📜 **Traza de Auditoría Completa**
- Almacenamiento S3 inmutable con retención configurable
- Eventos JSON estructurados con atribución de actor
- Registro listo para cumplimiento de todos los eventos del ciclo de vida

## Tecnología Utilizada

### Servicios Principales de AWS
- **Amazon EventBridge**: Ingestión y enrutamiento de eventos
- **AWS Lambda**: Computación serverless para toda la lógica de aplicación
- **AWS Step Functions**: Orquestación de flujo de trabajo con estados de espera HITL
- **Amazon Bedrock**: Diagnóstico y análisis basado en LLM
- **AWS Systems Manager (SSM)**: Ejecución y automatización de runbooks
- **Amazon S3**: Almacenamiento de traza de auditoría inmutable
- **Amazon CloudWatch**: Monitoreo, registro y verificación de salud
- **AWS IAM**: Control de acceso basado en roles y gestión de permisos

### Stack de Desarrollo
- **Python 3.11+**: Entorno de ejecución principal de Lambda
- **AWS CDK/CloudFormation**: Infraestructura como Código
- **pytest**: Pruebas unitarias y de integración
- **GitHub Actions**: automatización de pipeline CI/CD

## Estado del Proyecto

### Progreso de Kiro University

#### Completado
- [x] Definición del Proyecto
- [x] Requisitos
- [x] Diseño Técnico
- [x] Tareas de Implementación
- [x] Documentos de Guía
- [x] Kiro Hooks
- [x] Demostración de la Lección 3
- [x] Propiedades PBT Definidas
- [x] PBT-001 Límites de Puntuación de Riesgo Ejecutadas
- [x] PBT-002 Independencia de Confianza de IA Ejecutada
- [x] 200 Casos PBT Generados Pasados

#### Pendiente
- [ ] Ejecución PBT Seguridad HITL
- [ ] Ejecución PBT Ciclo de Vida de Recuperación
- [ ] Implementación de Infraestructura como Código
- [ ] Componentes Lambda Principales
- [ ] Flujo de Trabajo HITL
- [ ] remediación de Servicio SSM
- [ ] verificación de Salud
- [ ] Sistema de Auditoría Completo
- [ ] Demostración End-to-End Final

**Fase Actual**: Desarrollo MVP  
**Objetivo**: Escenario único de remediación completa (reinicio de servicio crítico)

### Alcance MVP:
- ✅ Detección de falla de servicio crítico mediante Alarmas de CloudWatch
- ✅ Creación de incidente y recopilación de evidencia
- ✅ Diagnóstico asistido por IA mediante Bedrock
- ✅ Evaluación de riesgo e identificación de Runbooks SSM
- ✅ Flujo de trabajo de aprobación HITL con gestión de tiempo de espera
- ✅ remediación a nivel de servicio mediante SSM (no reinicio de instancia)
- ✅ verificación de salud independiente
- ✅ Traza de auditoría inmutable (retención de 30 días MVP)

## Lecciones de Kiro University

### Lección 3: Kiro Hooks para Controles de Calidad

**Estado**: ✅ Completado

Implementados tres Kiro hooks para aplicar controles de calidad y límites de seguridad:

#### Hook de Puerta de Entrada Python
- **Archivo**: `.kiro/hooks/python-quality-gate.json`
- **Disparador**: `PostFileSave`
- **Coincidencia**: `\.py$`
- **Tipo de Acción**: `agent`
- **Propósito**: Realiza validación de calidad Python en archivos modificados por Kiro. Verifica sintaxis y herramientas de linting disponibles.

#### Hook de Guardia de Límite de Seguridad
- **Archivo**: `.kiro/hooks/security-boundary-guard.json`
- **Disparador**: `PreToolUse`
- **Tipo de Acción**: `agent`
- **Propósito**: Valida operaciones relevantes del agente contra el invariante de seguridad arquitectónica de SRE Copilot.

#### Hook de Validación Post-Tarea
- **Archivo**: `.kiro/hooks/post-task-validation.json`
- **Disparador**: `PostTaskExecution`
- **Tipo de Acción**: `agent`
- **Propósito**: Valida tareas de Spec completadas contra Requisitos, Diseño, Guía, restricciones de seguridad y pruebas relevantes.

### Lección 4: Pruebas Basadas en Propiedades

**Estado**: ✅ Completado

Implementadas Pruebas Basadas en Propiedades (PBT) para funciones del Risk Engine usando Hypothesis.

#### Propiedades PBT Definidas: 7

##### Propiedades Ejecutadas (2)
1. **PBT-001: Límites de Puntuación de Riesgo**
   - **Invariante**: `0 <= remediation_risk <= 100`
   - **Estado**: EXECUTED_PASS
   - **Casos**: 100 generados, 100 pasados, 0 fallados

2. **PBT-002: Independencia de Confianza de IA**
   - **Invariante**: Cambiar la Confianza de IA sola NO DEBE cambiar el Riesgo de remediación
   - **Estado**: EXECUTED_PASS
   - **Casos**: 100 generados, 100 pasados, 0 fallados

##### Propiedades Pendientes (5)
3. **PBT-003: Invariante de Seguridad REJECT**
   - **Invariante**: REJECT => NO SSM
   - **Estado**: EXECUTION_PENDING_IMPLEMENTATION

4. **PBT-004: Invariante de Seguridad TIMEOUT**
   - **Invariante**: TIMEOUT => NO SSM
   - **Estado**: EXECUTION_PENDING_IMPLEMENTATION

5. **PBT-005: Éxito de Ejecución No Es Recuperación**
   - **Invariante**: ÉXITO SSM + verificación de Salud != ÉXITO => estado != RESOLVED
   - **Estado**: EXECUTION_PENDING_IMPLEMENTATION

6. **PBT-006: resolución Requiere Recuperación Verificada**
   - **Invariante**: RESOLVED => ÉXITO de verificación de Salud
   - **Estado**: EXECUTION_PENDING_IMPLEMENTATION

7. **PBT-007: remediación de Servicio Idempotente**
   - **Invariante**: remediar(remediar(estado)) == remediar(estado)
   - **Estado**: EXECUTION_DEFERRED

#### Resumen de Ejecución PBT
- **Propiedades Definidas**: 7
- **Propiedades Ejecutadas**: 2
- **Casos Generados**: 200
- **Pasados**: 200
- **Fallados**: 0
- **Contrajemplos**: 0

## Comenzando

> **Nota**: Este proyecto está en desarrollo activo. Las instrucciones de instalación y despliegue se agregarán a medida que se implementen los componentes.

### Prerrequisitos
- Cuenta AWS con permisos apropiados
- Python 3.11+ y pip
- AWS CLI configurado
- Git para control de versiones

## Contribuciones

Agradecemos contribuciones que se alineen con los principios de seguridad arquitectónica del proyecto. Por favor revise lo siguiente antes de enviar cambios:

1. **Límites de Seguridad**: Cualquier cambio debe mantener la separación entre diagnóstico y ejecución
2. **Requisito HITL**: Ningún componente puede omitir la aprobación humana para operaciones que cambian el estado
3. **Traza de Auditoría**: Todos los eventos significativos deben registrarse en la traza de auditoría inmutable

## Licencia

Este proyecto es propietario y confidencial. Todos los derechos reservados.

---

<div align="center">
  <p><em>IA diagnostica. Humanos autorizan. Automatización remedia. La recuperación se verifica.</em></p>
  <p><a href="./README.md">Read in English</a></p>
</div>
