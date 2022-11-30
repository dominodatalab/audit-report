# Domino Project Audit Report

A lightweight tool to generate on-demand audit reports of code execution in a Domino project. 

## Scope

The audit report will aggregate select metadata on all Jobs executed in a Domino project.

## Installation

Add the following commands to a compute environment's pre-run setup script, or run them from a terminal in a workspace.

```bash
  git clone https://github.com/dominodatalab/audit-report.git
```

## Usage/Examples

From within a terminal in a workspace, or as a batch job inside a Domino project:
```bash
python audit.py
```

The report will be saved in the project as a `csv` to `/mnt/artifacts/` with the naming convenction: `audit-report_{project-name}_{YYYY-MM-DD_HH:MM:SSTZ}.csv`

Report fields and their order can be customized by editing `audit-report/report_config.ini`

## Support

For support please contact your Domino account team.

## Future Features
- Workspace metadata
- Multi-project support
- Job filtering
- Additional options in `report_config.ini`