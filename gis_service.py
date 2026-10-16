"""
GI4C GIS Service
Handles geospatial data processing and map generation
"""

import json
from typing import Dict, List
from models import GISLocation

# Try to import geospatial libraries
try:
    import geopandas as gpd
    from shapely.geometry import Point
    import folium
    GEOSPATIAL_AVAILABLE = True
except ImportError:
    GEOSPATIAL_AVAILABLE = False

class GISProcessor:
    """GIS and geospatial data processing for GI4C"""
    
    def __init__(self):
        self.default_center = [3.8488, 11.5021]  # Yaoundé, Cameroon
        self.default_zoom = 6
    
    def locations_to_geojson(self, locations: List[GISLocation]) -> Dict:
        """Convert database locations to GeoJSON format"""
        features = []
        
        for loc in locations:
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [loc.longitude, loc.latitude]
                },
                'properties': {
                    'id': loc.id,
                    'name': loc.name,
                    'type': loc.location_type,
                    'program_id': loc.program_id,
                    **(loc.properties or {})
                }
            }
            features.append(feature)
        
        return {
            'type': 'FeatureCollection',
            'features': features
        }
    
    def generate_map(self, locations: List[GISLocation]) -> str:
        """Generate interactive map HTML"""
        if GEOSPATIAL_AVAILABLE:
            return self._generate_folium_map(locations)
        else:
            return self._generate_demo_map(locations)
    
    def _generate_folium_map(self, locations: List[GISLocation]) -> str:
        """Generate map using Folium"""
        try:
            # Create map centered on first location or default
            if locations:
                center = [locations[0].latitude, locations[0].longitude]
            else:
                center = self.default_center
            
            m = folium.Map(
                location=center,
                zoom_start=self.default_zoom,
                tiles='OpenStreetMap'
            )
            
            # Add markers for each location
            for loc in locations:
                popup_content = f"""
                <b>{loc.name}</b><br>
                Type: {loc.location_type}<br>
                Program ID: {loc.program_id}
                """
                
                # Color based on location type
                color = self._get_marker_color(loc.location_type)
                
                folium.Marker(
                    location=[loc.latitude, loc.longitude],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color=color, icon='info-sign')
                ).add_to(m)
            
            # Add layer control
            folium.LayerControl().add_to(m)
            
            return m._repr_html_()
            
        except Exception as e:
            return self._generate_demo_map(locations)
    
    def _generate_demo_map(self, locations: List[GISLocation]) -> str:
        """Generate demo map placeholder"""
        return f"""
        <div style="padding: 20px; text-align: center; background: #f5f8fc; border-radius: 8px;">
            <h3>🗺️ Interactive GIS Map</h3>
            <p>Install geopandas and folium for full map functionality:</p>
            <code>pip install geopandas folium shapely</code>
            <p style="margin-top: 15px;">Current locations: {len(locations)}</p>
            <p>Map center: Yaoundé, Cameroon</p>
        </div>
        """
    
    def _get_marker_color(self, location_type: str) -> str:
        """Get marker color based on location type"""
        colors = {
            'project': 'green',
            'beneficiary': 'blue',
            'resource': 'orange',
            'risk': 'red',
            'health': 'pink',
            'education': 'purple'
        }
        return colors.get(location_type, 'blue')
    
    def calculate_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """Calculate distance between two points (Haversine formula)"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth's radius in km
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def find_nearby_locations(self, lat: float, lon: float, 
                              radius_km: float = 10) -> List[Dict]:
        """Find locations within a radius of a point"""
        try:
            locations = GISLocation.query.all()
            nearby = []
            
            for loc in locations:
                distance = self.calculate_distance(lat, lon, loc.latitude, loc.longitude)
                if distance <= radius_km:
                    nearby.append({
                        'id': loc.id,
                        'name': loc.name,
                        'type': loc.location_type,
                        'distance_km': round(distance, 2),
                        'latitude': loc.latitude,
                        'longitude': loc.longitude
                    })
            
            # Sort by distance
            nearby.sort(key=lambda x: x['distance_km'])
            
            return nearby
        except Exception as e:
            return []
    
    def generate_heatmap(self, locations: List[GISLocation]) -> str:
        """Generate heatmap visualization"""
        if not GEOSPATIAL_AVAILABLE:
            return self._generate_demo_heatmap(locations)
        
        try:
            from folium.plugins import HeatMap
            
            if locations:
                center = [locations[0].latitude, locations[0].longitude]
            else:
                center = self.default_center
            
            m = folium.Map(location=center, zoom_start=self.default_zoom)
            
            # Prepare heat data
            heat_data = [[loc.latitude, loc.longitude] for loc in locations]
            
            # Add heatmap
            HeatMap(heat_data, radius=15).add_to(m)
            
            return m._repr_html_()
            
        except Exception as e:
            return self._generate_demo_heatmap(locations)
    
    def _generate_demo_heatmap(self, locations: List[GISLocation]) -> str:
        """Generate demo heatmap placeholder"""
        return f"""
        <div style="padding: 20px; text-align: center; background: #f5f8fc; border-radius: 8px;">
            <h3>🔥 Heat Map Visualization</h3>
            <p>Install folium for heatmap functionality</p>
            <p style="margin-top: 15px;">Data points: {len(locations)}</p>
        </div>
        """
    
    def create_vulnerability_map(self, risk_data: List[Dict]) -> str:
        """Create vulnerability/risk map"""
        if not GEOSPATIAL_AVAILABLE:
            return """
            <div style="padding: 20px; text-align: center; background: #f5f8fc; border-radius: 8px;">
                <h3>⚠️ Vulnerability Map</h3>
                <p>Install geopandas and folium for vulnerability mapping</p>
            </div>
            """
        
        try:
            from folium.plugins import HeatMap
            
            m = folium.Map(location=self.default_center, zoom_start=self.default_zoom)
            
            # Prepare risk data with intensity weights
            heat_data = []
            for item in risk_data:
                heat_data.append([
                    item['latitude'],
                    item['longitude'],
                    item.get('risk_level', 1)
                ])
            
            # Add weighted heatmap
            HeatMap(heat_data, radius=20, max_zoom=12).add_to(m)
            
            return m._repr_html_()
            
        except Exception as e:
            return "Error generating vulnerability map"
    
    def export_geojson(self, locations: List[GISLocation], filename: str = None):
        """Export locations to GeoJSON file"""
        geojson = self.locations_to_geojson(locations)
        
        if filename:
            with open(filename, 'w') as f:
                json.dump(geojson, f, indent=2)
            return f"Exported to {filename}"
        else:
            return json.dumps(geojson, indent=2)
    
    def import_geojson(self, geojson_data: Dict) -> List[GISLocation]:
        """Import locations from GeoJSON"""
        from models import db
        
        locations = []
        
        for feature in geojson.get('features', []):
            geometry = feature.get('geometry', {})
            properties = feature.get('properties', {})
            
            if geometry.get('type') == 'Point':
                coords = geometry.get('coordinates', [])
                if len(coords) >= 2:
                    location = GISLocation(
                        name=properties.get('name'),
                        latitude=coords[1],
                        longitude=coords[0],
                        location_type=properties.get('type', 'project'),
                        program_id=properties.get('program_id'),
                        properties=properties
                    )
                    locations.append(location)
                    db.session.add(location)
        
        db.session.commit()
        return locations
