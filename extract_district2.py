from pymongo import MongoClient
import re

def extract_district(location):
    """Extract district name from location string"""
    if not location:
        return None
    
    return location.split(',')[0]
    return None


def update_properties():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['real_estate']
    collection = db['properties2']
    
    # Statistics counters
    total_records = 0
    updated_records = 0
    missing_district = 0

    for item in collection.find():
        total_records += 1
        updates = {}
        
        # Extract and add district
        location = item.get('location')
        district = extract_district(location)
        if district:
            updates['district'] = district
        else:
            missing_district += 1
            
        # Update document if we have changes
        if updates:
            collection.update_one(
                {'_id': item['_id']},
                {'$set': updates}
            )
            updated_records += 1

    # Print statistics
    print(f"\nProcessing Statistics:")
    print(f"Total records processed: {total_records}")
    print(f"Records updated: {updated_records}")
    print(f"Records missing district: {missing_district}")
    
    # Print sample of distinct districts
    districts = collection.distinct('district')
    print("\nDistinct districts found:")
    for district in sorted(filter(None, districts)):
        count = collection.count_documents({'district': district})
        print(f"{district}: {count} properties")

if __name__ == "__main__":
    update_properties()