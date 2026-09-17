from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests
import pandas as pd

app = FastAPI()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': '*/*', 
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.nseindia.com/option-chain'
}

@app.get("/api/nifty-oi")
def get_oi_data(symbol: str = "NIFTY"):
    session = requests.Session()
    try:
        # Initialize session cookies
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
        
        # Get Expiries
        c_res = session.get(f"https://www.nseindia.com/api/option-chain-contract-info?symbol={symbol}", headers=headers, timeout=5)
        expiries = c_res.json().get("expiryDates", [])
        
        if not expiries:
            return JSONResponse({"error": "No expiries found"}, status_code=500)
            
        # Fetch Option Chain
        chain_res = session.get(f"https://www.nseindia.com/api/option-chain-v3?type=Indices&symbol={symbol}&expiry={expiries[0]}", headers=headers, timeout=5)
        data = chain_res.json()
        
        records = data.get('records', {}).get('data', [])
        spot_price = data.get('records', {}).get('underlyingValue', 0.0)
        
        # Format data for the frontend chart
        clean_data = []
        for row in records:
            if row.get("expiryDate") == expiries[0]:
                clean_data.append({
                    "strike": row.get("strikePrice"),
                    "ce_oi": row.get("CE", {}).get("openInterest", 0),
                    "pe_oi": row.get("PE", {}).get("openInterest", 0)
                })
                
        return {
            "symbol": symbol,
            "spot_price": spot_price,
            "data": clean_data
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)