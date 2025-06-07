import requests

def get_realtime_usd_to_thb():
    try:
        url = "https://api.exchangerate.host/latest?base=USD&symbols=THB"
        response = requests.get(url)
        data = response.json()
        print("API response:", data)

        # ตรวจสอบว่ามีข้อมูลและสำเร็จจริงหรือไม่
        if data.get("success") and "THB" in data.get("rates", {}):
            return data["rates"]["THB"]
        else:
            raise ValueError("Missing 'THB' in rates or 'success' is False")
    except Exception as e:
        print("Error fetching exchange rate:", e)
        return 35.0  # fallback default

# ทดสอบ
if __name__ == "__main__":
    rate = get_realtime_usd_to_thb()
    print(f"Current USD to THB rate: {rate}")
