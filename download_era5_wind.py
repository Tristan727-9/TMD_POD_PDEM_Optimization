import cdsapi

dataset = "reanalysis-era5-single-levels"
request = {
    "product_type": ["reanalysis"],
    "variable": [
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
    ],
    "year": ["2024"],
    "month": ["04", "05"],
    "day": [
        "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
        "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15",
    ],
    "time": [
        "00:00", "01:00", "02:00", "03:00", "04:00", "05:00",
        "06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00", "21:00", "22:00", "23:00",
    ],
    "data_format": "netcdf",
    "download_format": "unarchived",
    # Bounding box [North, West, South, East] — A Coruña, Spain
    "area": [43.45, -8.55, 43.20, -8.30],
}

client = cdsapi.Client()
client.retrieve(dataset, request).download()
