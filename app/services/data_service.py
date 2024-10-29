from typing import Dict, Any, List
import csv
from io import StringIO
from app import db
from app.models import DataType, AssetType, Building, Department

class DataImportService:
    def __init__(self):
        self.models = {
            DataType.ASSET_TYPE.value: AssetType,
            DataType.BUILDING.value: Building,
            DataType.DEPARTMENT.value: Department
        }
    
    def validate_csv_structure(self, model_type: str, headers: List[str]) -> None:
        """Validate CSV headers match model requirements"""
        model_class = self.models.get(model_type)
        if not model_class:
            raise ValueError(f"Invalid model type: {model_type}")
        
        metadata = model_class.get_metadata()
        required_fields = metadata['required_fields']
        missing_headers = [h for h in required_fields if h not in headers]
        
        if missing_headers:
            raise ValueError(f"Missing required columns: {', '.join(missing_headers)}")
    
    def validate_row_data(self, model_type: str, row_data: Dict[str, Any]) -> None:
        """Validate individual row data"""
        model_class = self.models.get(model_type)
        metadata = model_class.get_metadata()
        
        # Validate required fields
        for field in metadata['required_fields']:
            if field not in row_data or not row_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Apply validation rules
        for field, validator in metadata['validation_rules'].items():
            if not validator(row_data[field]):
                raise ValueError(f"Validation failed for {field}: {row_data[field]}")
    
    def import_data(self, model_type: str, csv_data: str, import_mode: str = 'append') -> Dict[str, int]:
        """Import data from CSV"""
        model_class = self.models.get(model_type)
        if not model_class:
            raise ValueError(f"Invalid model type: {model_type}")
        
        csv_file = StringIO(csv_data)
        csv_reader = csv.DictReader(csv_file)
        
        # Validate CSV structure
        self.validate_csv_structure(model_type, csv_reader.fieldnames)
        
        stats = {'added': 0, 'updated': 0, 'skipped': 0}
        
        try:
            # Handle overwrite mode
            if import_mode == 'overwrite':
                model_class.query.delete()
                db.session.commit()
            
            # Process each row
            for row in csv_reader:
                try:
                    self.validate_row_data(model_type, row)
                    
                    if import_mode == 'replace':
                        self._handle_replace_mode(model_class, row, stats)
                    elif import_mode == 'append':
                        self._handle_append_mode(model_class, row, stats)
                    else:  # overwrite mode
                        self._handle_overwrite_mode(model_class, row, stats)
                        
                except ValueError as e:
                    raise ValueError(f"Error in row {csv_reader.line_num}: {str(e)}")
            
            db.session.commit()
            return stats
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def _handle_replace_mode(self, model_class, row: Dict[str, Any], stats: Dict[str, int]) -> None:
        existing = model_class.query.filter_by(code=row['code']).first()
        if existing:
            for key, value in row.items():
                setattr(existing, key, value)
            stats['updated'] += 1
        else:
            new_record = model_class(**row)
            db.session.add(new_record)
            stats['added'] += 1
    
    def _handle_append_mode(self, model_class, row: Dict[str, Any], stats: Dict[str, int]) -> None:
        existing = model_class.query.filter(
            db.or_(
                model_class.code == row['code'],
                db.and_(
                    model_class.title == row['title'],
                    model_class.code == row['code']
                )
            )
        ).first()
        
        if existing:
            stats['skipped'] += 1
        else:
            new_record = model_class(**row)
            db.session.add(new_record)
            stats['added'] += 1
    
    def _handle_overwrite_mode(self, model_class, row: Dict[str, Any], stats: Dict[str, int]) -> None:
        new_record = model_class(**row)
        db.session.add(new_record)
        stats['added'] += 1
