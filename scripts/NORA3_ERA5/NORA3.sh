#!/usr/bin/bash

time python NORA3_ERA5.py -i stationlist.csv -p integral_of_toa_net_downward_shortwave_flux_wrt_time -o integral_of_toa_net_downward_shortwave_flux_wrt_time.nc -s 2016-01-01T00:00 -e 2020-12-31T23:00
time python NORA3_ERA5.py -i stationlist.csv -p integral_of_surface_net_downward_shortwave_flux_wrt_time -o integral_of_surface_net_downward_shortwave_flux_wrt_time.nc -s 2016-01-01T00:00 -e 2020-12-31T23:00
time python NORA3_ERA5.py -i stationlist.csv -p integral_of_surface_downwelling_shortwave_flux_in_air_wrt_time -o integral_of_surface_downwelling_shortwave_flux_in_air_wrt_time.nc -s 2016-01-01T00:00 -e 2020-12-31T23:00
time python NORA3_ERA5.py -i stationlist.csv -p air_temperature_2m -o air_temperature_2m.nc -s 2016-01-01T00:00 -e 2020-12-31T23:00
time python NORA3_ERA5.py -i stationlist.csv -p cloud_area_fraction -o cloud_area_fraction.nc -s 2016-01-01T00:00 -e 2020-12-31T23:00
time python NORA3_ERA5.py -i stationlist.csv -p convective_cloud_area_fraction -o convective_cloud_area_fraction.nc -s 2016-01-01T00:00 -e 2020-12-31T23:00
time python NORA3_ERA5.py -i stationlist.csv -p high_type_cloud_area_fraction -o high_type_cloud_area_fraction.nc -s 2016-01-01T00:00 -e 2020-12-31T23:00
time python NORA3_ERA5.py -i stationlist.csv -p medium_type_cloud_area_fraction -o medium_type_cloud_area_fraction.nc -s 2016-01-01T00:00 -e 2020-12-31T23:00
time python NORA3_ERA5.py -i stationlist.csv -p low_type_cloud_area_fraction -o low_type_cloud_area_fraction.nc -s 2016-01-01T00:00 -e 2020-12-31T23:00
time python NORA3_ERA5.py -i stationlist.csv -p snowfall_amount_acc -o snowfall_amount_acc.nc -s 2016-01-01T00:00 -e 2020-12-31T23:00
time python NORA3_ERA5.py -i stationlist.csv -p precipitation_amount_acc -o precipitation_amount_acc.nc -s 2016-01-01T00:00 -e 2020-12-31T23:00
time python NORA3_ERA5.py -i stationlist.csv -p lwe_thickness_of_atmosphere_mass_content_of_water_vapor -o lwe_thickness_of_atmosphere_mass_content_of_water_vapor.nc -s 2016-01-01T00:00 -e 2020-12-31T23:00
time python NORA3_ERA5.py -i stationlist.csv -p ASN_VEG -o ASN_VEG.nc -s 2016-01-01T00:00 -e 2020-12-31T23:00
time python NORA3_ERA5.py -i stationlist.csv -p TALB_ISBA -o TALB_ISBA.nc -s 2016-01-01T00:00 -e 2020-12-31T23:00
time python NORA3_ERA5.py -i stationlist.csv -p LAI -o LAI.nc -s 2016-01-01T00:00 -e 2020-12-31T23:00
time python NORA3_ERA5.py -i stationlist.csv -p VEG -o VEG.nc -s 2016-01-01T00:00 -e 2020-12-31T23:00
