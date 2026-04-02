from flask import Flask, Response
import requests

app = Flask(__name__)

API_URL = "https://sceyeballoontracker.web.app/api?flight_id=SE2&auth=public_default_key"

def get_kml_color(alt_ft):
    if alt_ft < 20000:      return "ffff0000"
    elif alt_ft < 40000:    return "ffff8800"
    elif alt_ft < 60000:    return "ff00ff00"
    elif alt_ft < 80000:    return "ff00ffff"
    else:                   return "ff0000ff"

@app.route('/SE2_Live_Flight.kml')
def live_kml():
    try:
        r = requests.get(API_URL, timeout=15)
        r.raise_for_status()
        data = r.json()

        lat = data.get('lat')
        lon = data.get('lng')
        alt = data.get('alt')
        speed = data.get('speed')
        timestamp = data.get('time')

        kml = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>SE2 Live Balloon Flight</name>
    <description>Live from SCEye API • Auto-updates every 60s</description>

    <Style id="pathStyle">
      <LineStyle><color>ff00ffcc</color><width>6</width></LineStyle>
    </Style>

    <Style id="pointStyle">
      <IconStyle><scale>0.7</scale><Icon><href>https://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle>
    </Style>

    <Placemark>
      <name>Flight Path</name>
      <styleUrl>#pathStyle</styleUrl>
      <LineString>
        <tessellate>1</tessellate>
        <altitudeMode>absolute</altitudeMode>
        <coordinates>{lon},{lat},{alt * 0.3048}</coordinates>
      </LineString>
    </Placemark>

    <Placemark>
      <name>🚀 SE2 Current Position</name>
      <description><![CDATA[<b>LIVE POSITION</b><br>
Time: {timestamp} UTC<br>
Altitude: {alt:.0f} ft<br>
Speed: {speed:.1f} knots]]></description>
      <Style>
        <IconStyle><scale>1.5</scale><Icon><href>https://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon></IconStyle>
      </Style>
      <Point>
        <altitudeMode>absolute</altitudeMode>
        <coordinates>{lon},{lat},{alt * 0.3048}</coordinates>
      </Point>
    </Placemark>

    <Folder>
      <name>Altitude Legend</name>
      <Placemark>
        <name>Color Scale</name>
        <description><![CDATA[<b>Altitude Color Legend</b><br><br>
<span style="color:#0000ff">■</span> &lt; 20,000 ft<br>
<span style="color:#ff8800">■</span> 20k–40k ft<br>
<span style="color:#00ff00">■</span> 40k–60k ft<br>
<span style="color:#00ffff">■</span> 60k–80k ft<br>
<span style="color:#ff0000">■</span> &gt; 80,000 ft]]></description>
      </Placemark>
    </Folder>
  </Document>
</kml>'''
        return Response(kml, mimetype='application/vnd.google-earth.kml+xml')

    except Exception as e:
        error = f"Error fetching API: {str(e)}"
        return Response(f'<?xml version="1.0"?><kml><Document><name>Error</name><description>{error}</description></Document></kml>', mimetype='application/vnd.google-earth.kml+xml')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
