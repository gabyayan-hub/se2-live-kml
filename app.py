from flask import Flask, Response
import requests
from datetime import datetime

app = Flask(__name__)

API_URL = "https://sceyeballoontracker.web.app/api?flight_id=SE2&auth=public_default_key"

# Store last 500 points in memory
points_history = []

def get_kml_color(alt_ft):
    if alt_ft < 20000:      return "ffff0000"   # blue
    elif alt_ft < 40000:    return "ffff8800"   # cyan
    elif alt_ft < 60000:    return "ff00ff00"   # green
    elif alt_ft < 80000:    return "ff00ffff"   # yellow
    else:                   return "ff0000ff"   # red

@app.route('/SE2_Live_Flight.kml')
def live_kml():
    global points_history
    try:
        r = requests.get(API_URL, timeout=15)
        r.raise_for_status()
        data = r.json()

        lat = data.get('lat')
        lon = data.get('lng')
        alt = data.get('alt')
        speed = data.get('speed')
        timestamp = data.get('time')

        # Add new point
        new_point = (lat, lon, alt, speed, timestamp)
        points_history.append(new_point)
        if len(points_history) > 500:
            points_history.pop(0)

        # Build full KML
        kml = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>SE2 Live Balloon Flight</name>
    <description>Live from SCEye API • Updated {datetime.now().strftime("%H:%M:%S")} UTC</description>

    <!-- Path Style -->
    <Style id="pathStyle">
      <LineStyle><color>ff00ffcc</color><width>6</width></LineStyle>
    </Style>

    <!-- Point Style (base) -->
    <Style id="pointStyle">
      <IconStyle><scale>0.6</scale><Icon><href>https://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle>
      <LabelStyle><scale>0</scale></LabelStyle>
    </Style>

    <!-- Full Flight Path -->
    <Placemark>
      <name>Flight Path</name>
      <styleUrl>#pathStyle</styleUrl>
      <LineString>
        <tessellate>1</tessellate>
        <altitudeMode>absolute</altitudeMode>
        <coordinates>
'''
        for p in points_history:
            kml += f"          {p[1]},{p[0]},{p[2]*0.3048}\n"
        kml += '''        </coordinates>
      </LineString>
    </Placemark>

    <!-- Colored Historical Points -->
    <Folder>
      <name>Detailed Track Points</name>
      <open>0</open>
'''
        for p in points_history:
            color = get_kml_color(p[2])
            kml += f'''      <Placemark>
        <description><![CDATA[<b>{p[4]}</b><br>Altitude: {p[2]:.0f} ft<br>Speed: {p[3]:.1f} knots]]></description>
        <styleUrl>#pointStyle</styleUrl>
        <Style>
          <IconStyle>
            <color>{color}</color>
            <scale>0.6</scale>
            <Icon><href>https://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon>
          </IconStyle>
        </Style>
        <Point>
          <altitudeMode>absolute</altitudeMode>
          <coordinates>{p[1]},{p[0]},{p[2]*0.3048}</coordinates>
        </Point>
      </Placemark>
'''
        kml += '''    </Folder>

    <!-- Current Position -->
    <Placemark>
      <name>🚀 SE2 Current Position</name>
      <description><![CDATA[<b>LIVE POSITION</b><br>
Time: ''' + timestamp + ''' UTC<br>
Altitude: ''' + f"{alt:.0f}" + ''' ft<br>
Speed: ''' + f"{speed:.1f}" + ''' knots<br>
Last updated: ''' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ''']]></description>
      <Style>
        <IconStyle><scale>1.5</scale><Icon><href>https://maps.google.com/mapfiles/kml/shapes/airports.png</href></Icon></IconStyle>
      </Style>
      <Point>
        <altitudeMode>absolute</altitudeMode>
        <coordinates>''' + f"{lon},{lat},{alt*0.3048}" + '''</coordinates>
      </Point>
    </Placemark>

    <!-- Altitude Legend -->
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
        error_kml = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml><Document><name>Error</name><description>Failed to fetch API: {str(e)}</description></Document></kml>'''
        return Response(error_kml, mimetype='application/vnd.google-earth.kml+xml')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
