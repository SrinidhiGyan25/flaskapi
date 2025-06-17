import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from naukri_scrape import get_naukri_jobs

# ----------- Location Normalization -----------
def normalize_location(location):
    known_locations = {
        "bangalore": "Bangalore",
        "bengaluru": "Bangalore",
        "mumbai": "Mumbai",
        "delhi": "Delhi",
        "pune": "Pune",
        "noida": "Noida",
        "hyderabad": "Hyderabad",
        "chennai": "Chennai",
        "gurgaon": "Gurgaon",
        "kolkata": "Kolkata"
    }

    cleaned_location = location.lower().replace("/", " ")
    cleaned_location = re.sub(r"[(),\-{}\[\]]", " ", cleaned_location)
    cleaned_location = re.sub(r"\s+", " ", cleaned_location).strip()
    words = cleaned_location.split()

    for word in words:
        if word in known_locations:
            return known_locations[word]

    return words[0].capitalize() if words else location.title()


def expand_locations(df):
    rows = []
    for _, row in df.iterrows():
        locations = str(row['Location']).split(',')
        for loc in locations:
            new_row = row.copy()
            new_row['Location'] = normalize_location(loc.strip())
            rows.append(new_row)
    return pd.DataFrame(rows)

# ----------- India Map Heatmap Generation -----------
def get_city_coordinates():
    """Return coordinates for major Indian cities"""
    return {
        'Mumbai': (19.0760, 72.8777),
        'Delhi': (28.7041, 77.1025),
        'Bangalore': (12.9716, 77.5946),
        'Hyderabad': (17.3850, 78.4867),
        'Chennai': (13.0827, 80.2707),
        'Kolkata': (22.5726, 88.3639),
        'Pune': (18.5204, 73.8567),
        'Ahmedabad': (23.0225, 72.5714),
        'Jaipur': (26.9124, 75.7873),
        'Surat': (21.1702, 72.8311),
        'Lucknow': (26.8467, 80.9462),
        'Kanpur': (26.4499, 80.3319),
        'Nagpur': (21.1458, 79.0882),
        'Indore': (22.7196, 75.8577),
        'Thane': (19.2183, 72.9781),
        'Bhopal': (23.2599, 77.4126),
        'Visakhapatnam': (17.6868, 83.2185),
        'Pimpri': (18.6298, 73.7997),
        'Patna': (25.5941, 85.1376),
        'Vadodara': (22.3072, 73.1812),
        'Ghaziabad': (28.6692, 77.4538),
        'Ludhiana': (30.9010, 75.8573),
        'Agra': (27.1767, 78.0081),
        'Nashik': (19.9975, 73.7898),
        'Faridabad': (28.4089, 77.3178),
        'Meerut': (28.9845, 77.7064),
        'Rajkot': (22.3039, 70.8022),
        'Kalyan': (19.2437, 73.1355),
        'Vasai': (19.4916, 72.8054),
        'Varanasi': (25.3176, 82.9739),
        'Srinagar': (34.0837, 74.7973),
        'Aurangabad': (19.8762, 75.3433),
        'Dhanbad': (23.7957, 86.4304),
        'Amritsar': (31.6340, 74.8723),
        'Allahabad': (25.4358, 81.8463),
        'Ranchi': (23.3441, 85.3096),
        'Howrah': (22.5958, 88.2636),
        'Coimbatore': (11.0168, 76.9558),
        'Jabalpur': (23.1815, 79.9864),
        'Gwalior': (26.2183, 78.1828),
        'Vijayawada': (16.5062, 80.6480),
        'Jodhpur': (26.2389, 73.0243),
        'Madurai': (9.9252, 78.1198),
        'Raipur': (21.2514, 81.6296),
        'Kota': (25.2138, 75.8648),
        'Gurgaon': (28.4595, 77.0266),
        'Noida': (28.5355, 77.3910),
        'Chandigarh': (30.7333, 76.7794),
        'Mysore': (12.2958, 76.6394),
        'Bareilly': (28.3670, 79.4304),
        'Aligarh': (27.8974, 78.0880),
        'Tiruchirappalli': (10.7905, 78.7047),
        'Bhubaneswar': (20.2961, 85.8245),
        'Salem': (11.6643, 78.1460),
        'Thiruvananthapuram': (8.5241, 76.9366),
        'Bhilai': (21.1938, 81.3509),
        'Cuttack': (20.4625, 85.8828)
    }

def create_india_map_heatmap(df, job_title):
    """Create a heatmap on India map showing job distribution"""
    try:
        import folium
        from folium.plugins import HeatMap
        import numpy as np
        
        # Get location counts
        location_counts = df['Location'].value_counts()
        city_coords = get_city_coordinates()
        
        # Create base map centered on India
        india_map = folium.Map(
            location=[20.5937, 78.9629],  # Center of India
            zoom_start=5,
            tiles='OpenStreetMap'
        )
        
        # Prepare data for heatmap
        heat_data = []
        marker_data = []
        
        for location, count in location_counts.items():
            if location in city_coords:
                lat, lon = city_coords[location]
                # Add multiple points based on job count for better heatmap intensity
                intensity = min(count, 50)  # Cap intensity for better visualization
                for _ in range(intensity):
                    heat_data.append([lat, lon, 1])
                marker_data.append([lat, lon, location, count])
        
        # Add heatmap layer
        if heat_data:
           gradient = {'0.2': 'blue', '0.4': 'lime', '0.6': 'orange', '1.0': 'red'}
           HeatMap(heat_data, radius=15, blur=10, gradient=gradient).add_to(india_map)

        
        # Add markers with job counts
        for lat, lon, location, count in marker_data:
            folium.CircleMarker(
                location=[lat, lon],
                radius=min(count/2 + 5, 20),  # Size based on job count
                popup=f'<b>{location}</b><br>{count} jobs',
                tooltip=f'{location}: {count} jobs',
                color='darkred',
                fill=True,
                fillColor='red',
                fillOpacity=0.7
            ).add_to(india_map)
        
        # Save the map
        map_file = f"{job_title.replace(' ', '_')}_india_heatmap.html"
        india_map.save(map_file)
        
        # print(f"🗺️ India map heatmap generated: {map_file}")
        return map_file
        
    except ImportError:
        print("❌ Folium not installed. Installing folium for map generation...")
        print("Please run: pip install folium")
        return None

def create_static_india_heatmap(df, job_title):
    """Create a static heatmap on India map using matplotlib"""
    try:
        import numpy as np
        from matplotlib.patches import Circle
        
        # Get location counts and coordinates
        location_counts = df['Location'].value_counts()
        city_coords = get_city_coordinates()
        
        # Create figure
        plt.figure(figsize=(15, 12))
        
        # India boundary coordinates (simplified)
        india_boundary = {
            'lat_min': 6, 'lat_max': 37,
            'lon_min': 68, 'lon_max': 98
        }
        
        # Create the plot
        ax = plt.gca()
        ax.set_xlim(india_boundary['lon_min'], india_boundary['lon_max'])
        ax.set_ylim(india_boundary['lat_min'], india_boundary['lat_max'])
        
        # Plot cities with job counts
        max_jobs = location_counts.max() if len(location_counts) > 0 else 1
        
        for location, count in location_counts.items():
            if location in city_coords:
                lat, lon = city_coords[location]
                
                # Calculate size and color based on job count
                size = (count / max_jobs) * 500 + 50
                color_intensity = count / max_jobs
                
                # Plot circle
                circle = Circle((lon, lat), radius=0.5, 
                              alpha=0.6 + 0.4 * color_intensity,
                              color=plt.cm.YlOrRd(color_intensity))
                ax.add_patch(circle)
                
                # Add city name and count
                plt.annotate(f'{location}\n({count})', 
                           (lon, lat), 
                           xytext=(5, 5), 
                           textcoords='offset points',
                           fontsize=8,
                           bbox=dict(boxstyle='round,pad=0.3', 
                                   facecolor='white', 
                                   alpha=0.8))
        
        # Styling
        plt.title(f'{job_title} Jobs Distribution Across India', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Longitude', fontsize=12)
        plt.ylabel('Latitude', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Add a colorbar
        sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd, 
                                  norm=plt.Normalize(vmin=0, vmax=max_jobs))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, shrink=0.6)
        cbar.set_label('Number of Jobs', rotation=270, labelpad=20)
        
        plt.tight_layout()
        
        # Save the static heatmap
        static_map_file = f"{job_title.replace(' ', '_')}_static_india_heatmap.png"
        plt.savefig(static_map_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # print(f"🗺️ Static India heatmap generated: {static_map_file}")
        return static_map_file
        
    except Exception as e:
        print(f"❌ Error creating static heatmap: {e}")
        return None

def create_location_heatmap(df, job_title):
    """Create a bar chart showing job distribution by location"""
    
    # Count jobs by location
    location_counts = df['Location'].value_counts().head(15)
    
    plt.figure(figsize=(14, 8))
    
    # Create horizontal bar chart for better readability
    bars = plt.barh(range(len(location_counts)), location_counts.values, 
                    color=plt.cm.viridis(np.linspace(0, 1, len(location_counts))))
    
    # Customize the plot
    plt.yticks(range(len(location_counts)), location_counts.index)
    plt.xlabel('Number of Jobs', fontsize=12, fontweight='bold')
    plt.title(f'{job_title} Jobs Distribution - Top 15 Locations', 
              fontsize=16, fontweight='bold', pad=20)
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, location_counts.values)):
        plt.text(value + max(location_counts.values) * 0.01, i, 
                str(value), va='center', fontweight='bold')
    
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    
    # Save the chart
    chart_file = f"{job_title.replace(' ', '_')}_location_chart.png"
    plt.savefig(chart_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    # print(f"📊 Location chart generated: {chart_file}")
    return chart_file

# ----------- Main HTML Report Generation -----------
def generate_html_report(job_title="PCB Design", pages=2, create_heatmap=True):
    df = get_naukri_jobs(job_title, pages=pages)
    if df.empty:
        print("No jobs found.")
        return

    df = expand_locations(df)

    # Generate heatmaps if requested
    heatmap_files = []
    if create_heatmap:
        print("\n📈 Generating location visualizations...")
        
        # Create India map heatmap (interactive)
        india_map_file = create_india_map_heatmap(df, job_title)
        if india_map_file:
            heatmap_files.append(india_map_file)
        
        # Create static India heatmap
        static_map_file = create_static_india_heatmap(df, job_title)
        if static_map_file:
            heatmap_files.append(static_map_file)
        
        # Create location bar chart
        chart_file = create_location_heatmap(df, job_title)
        if chart_file:
            heatmap_files.append(chart_file)

    # Select and rename only required columns
    df_display = df[['Job Title', 'Location', 'Experience', 'Description']]
    
    # Generate location summary
    location_summary = df['Location'].value_counts().head(10)
    summary_html = "<h2>Top 10 Locations by Job Count</h2><ul>"
    for location, count in location_summary.items():
        summary_html += f"<li><strong>{location}</strong>: {count} jobs</li>"
    summary_html += "</ul>"

    html_content = f"""
    <html>
    <head>
        <title>{job_title} Jobs Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f9f9f9; }}
            h1 {{ color: #333; text-align: center; }}
            h2 {{ color: #555; border-bottom: 2px solid #007acc; padding-bottom: 5px; }}
            .summary {{ background-color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .heatmap-info {{ background-color: #e8f4f8; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; background-color: white; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #007acc; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            ul {{ line-height: 1.6; }}
            .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .stat-box {{ background-color: #007acc; color: white; padding: 15px; border-radius: 8px; text-align: center; }}
        </style>
    </head>
    <body>
        <h1>{job_title} Jobs Report</h1>
        
        <div class="stats">
            <div class="stat-box">
                <h3>Total Jobs Found</h3>
                <p style="font-size: 24px; margin: 0;">{len(df)}</p>
            </div>
            <div class="stat-box">
                <h3>Unique Locations</h3>
                <p style="font-size: 24px; margin: 0;">{df['Location'].nunique()}</p>
            </div>
        </div>
        
        {"<div class='heatmap-info'><strong>📊 Heatmap files generated:</strong><br>" + "<br>".join([f"• {file}" for file in heatmap_files]) + "</div>" if heatmap_files else ""}
        
        <div class="summary">
            {summary_html}
        </div>
        
        <h2>Detailed Job Listings</h2>
        {df_display.to_html(index=False, escape=False)}
    </body>
    </html>
    """

    output_file = f"{job_title.replace(' ', '_')}_report.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n✅ Report generated: {output_file}")
    if heatmap_files:
        print(f"📊 Heatmap files: {', '.join(heatmap_files)}")

# ----------- Run Script -----------
if __name__ == "__main__":
    job_title = input("Enter job title (e.g., PCB Design): ").strip()
    pages = int(input("Enter number of pages to scrape (e.g., 2): ").strip())
    create_heatmap = input("Generate location heatmap? (y/n, default: y): ").strip().lower()
    create_heatmap = create_heatmap != 'n'
    
    generate_html_report(job_title=job_title, pages=pages, create_heatmap=create_heatmap)