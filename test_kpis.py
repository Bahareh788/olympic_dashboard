#!/usr/bin/env python3

import requests
import json
import time

def test_kpis():
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test the strategic data API
        response = requests.get('http://localhost:5000/api/strategic-data')
        
        if response.status_code == 200:
            data = response.json()
            
            print("=== KPI Test Results ===")
            print(f"Medal Ratio: {data.get('kpi_medal_ratio', 'ERROR')}")
            print(f"Total Participants: {data['summary']['total_participants']:,}")
            print(f"Total Medals: {data['summary']['total_medals']:,}")
            print(f"Average Efficiency: {data['summary']['avg_efficiency']}%")
            print(f"Countries Count: {data['summary']['countries_count']}")
            
            # Calculate expected ratio
            if data['summary']['total_participants'] > 0:
                expected_ratio = data['summary']['total_medals'] / data['summary']['total_participants']
                print(f"Expected Ratio: {expected_ratio:.4f}")
                print(f"Actual Ratio: {data.get('kpi_medal_ratio', 'ERROR')}")
                
                if abs(expected_ratio - data.get('kpi_medal_ratio', 0)) < 0.0001:
                    print("✅ Medal ratio calculation is CORRECT")
                else:
                    print("❌ Medal ratio calculation is INCORRECT")
            
            print("\n=== Sample Data Validation ===")
            print(f"Participation Trend Records: {len(data.get('participation_trend', []))}")
            print(f"Medal Performance Records: {len(data.get('medal_performance', []))}")
            print(f"Efficiency Records: {len(data.get('medal_efficiency', []))}")
            
        else:
            print(f"API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_kpis() 