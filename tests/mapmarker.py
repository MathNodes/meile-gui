from kivy.app import App
from kivy.clock import Clock
from kivy_garden.mapview import MapView, MapMarker

class MapViewApp(App):
    def build(self):
        mapview = MapView(lat=50.6394, lon=3.057, zoom=11)
        mapview.map_source = "osm"
        m1 = MapMarker(lat=50.6394, lon=3.057)
        mapview.add_marker(m1)
        return mapview


MapViewApp().run()