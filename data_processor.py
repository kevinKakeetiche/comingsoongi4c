"""
GI4C Data Processor
Handles data processing, analytics, and report generation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
from models import Program, ImpactData, Donation, db

class DataProcessor:
    """Data processing and analytics for GI4C"""
    
    def __init__(self):
        pass
    
    def get_kpi_data(self) -> Dict:
        """Get key performance indicators from recorded programme data."""
        total_beneficiaries = db.session.query(
            db.func.sum(Program.beneficiaries)
        ).scalar()
        total_programs = Program.query.filter_by(status='active').count()
        total_donations = db.session.query(
            db.func.sum(Donation.amount)
        ).filter(Donation.status == 'completed').scalar()
        total_regions = db.session.query(
            db.func.count(db.distinct(Program.region))
        ).scalar()
        last_updated = db.session.query(
            db.func.max(Program.updated_at)
        ).scalar()

        return {
            'beneficiaries': int(total_beneficiaries) if total_beneficiaries is not None else None,
            'programs': total_programs,
            'regions': total_regions,
            'donations': float(total_donations) if total_donations is not None else None,
            'growth_rate': None,
            'last_updated': last_updated.isoformat() if last_updated else None
        }
    
    def get_impact_data(self) -> Dict:
        """Get recorded impact metrics and trends without demo fallbacks."""
        impact_records = ImpactData.query.all()
        if not impact_records:
            return {'metrics': {}, 'trends': [], 'total_metrics': 0}

        df = pd.DataFrame([{
            'metric': record.metric_name,
            'value': record.metric_value,
            'unit': record.metric_unit,
            'date': record.date_recorded,
            'region': record.region
        } for record in impact_records])

        metrics = df.groupby('metric')['value'].sum().to_dict()
        six_months_ago = datetime.utcnow().date() - timedelta(days=180)
        recent_data = df[df['date'] >= six_months_ago]
        trends = []
        for metric in recent_data['metric'].unique():
            metric_data = recent_data[recent_data['metric'] == metric].sort_values('date')
            trends.append({
                'metric': metric,
                'values': metric_data['value'].tolist(),
                'dates': [
                    date.isoformat() if hasattr(date, 'isoformat') else str(date)
                    for date in metric_data['date']
                ]
            })

        return {
            'metrics': metrics,
            'trends': trends,
            'total_metrics': len(metrics)
        }
    
    def generate_report(self, report_type: str, program_id: int = None) -> Dict:
        """Generate a report"""
        try:
            report_data = {
                'report_type': report_type,
                'generated_at': datetime.utcnow().isoformat(),
                'program_id': program_id
            }
            
            if report_type == 'situation':
                report_data.update(self._generate_situation_report(program_id))
            elif report_type == 'policy':
                report_data.update(self._generate_policy_report(program_id))
            elif report_type == 'warning':
                report_data.update(self._generate_warning_report(program_id))
            
            return report_data
        except Exception as e:
            raise Exception(f"Report generation failed: {str(e)}")
    
    def _generate_situation_report(self, program_id: int = None) -> Dict:
        """Summarize recorded programme data without inferred findings."""
        kpi = self.get_kpi_data()
        beneficiary_total = kpi['beneficiaries']
        program_total = kpi['programs']
        if beneficiary_total is None or program_total is None:
            summary = 'Data not yet available'
        else:
            summary = (
                f'GI4C programme records report {beneficiary_total} beneficiaries '
                f'across {program_total} active programmes.'
            )
        return {
            'title': 'Situation Report',
            'summary': summary,
            'key_findings': [],
            'recommendations': []
        }
    
    def _generate_policy_report(self, program_id: int = None) -> Dict:
        """Return a policy brief shell without unsupported impact claims."""
        return {
            'title': 'Policy Brief',
            'summary': 'Verified programme evidence is required before a policy analysis can be produced.',
            'key_findings': [],
            'recommendations': []
        }
    
    def _generate_warning_report(self, program_id: int = None) -> Dict:
        """Return an early warning shell until verified monitoring data exists."""
        return {
            'title': 'Early Warning Bulletin',
            'summary': 'Data not yet available',
            'alerts': [],
            'recommendations': []
        }
    
    def analyze_beneficiaries(self) -> Dict:
        """Aggregate recorded programme beneficiary fields."""
        programs = Program.query.all()
        by_region = {}
        by_program = {}
        known_totals = []

        for program in programs:
            if program.beneficiaries is not None:
                known_totals.append(program.beneficiaries)
                by_program[program.name] = program.beneficiaries
                if program.region:
                    by_region[program.region] = (
                        by_region.get(program.region, 0) + program.beneficiaries
                    )

        return {
            'total': sum(known_totals) if known_totals else None,
            'by_region': by_region,
            'by_program': by_program,
            'demographics': 'Data not yet available'
        }
    
    def export_data(self, data_type: str, format: str = 'csv') -> str:
        """Export data in specified format"""
        try:
            if data_type == 'programs':
                data = Program.query.all()
                df = pd.DataFrame([{
                    'name': p.name,
                    'category': p.category,
                    'beneficiaries': p.beneficiaries,
                    'region': p.region,
                    'status': p.status
                } for p in data])
            elif data_type == 'impact':
                data = ImpactData.query.all()
                df = pd.DataFrame([{
                    'metric': r.metric_name,
                    'value': r.metric_value,
                    'unit': r.metric_unit,
                    'date': r.date_recorded,
                    'region': r.region
                } for r in data])
            else:
                raise Exception(f"Unknown data type: {data_type}")
            
            if format == 'csv':
                return df.to_csv(index=False)
            elif format == 'json':
                return df.to_json(orient='records')
            else:
                raise Exception(f"Unsupported format: {format}")
                
        except Exception as e:
            raise Exception(f"Data export failed: {str(e)}")
