# mbta-actual-trip-times

This project is a tool meant to figure out the best ways people can get around on the T, and to give information on how fast and reliable certain routes are. By putting in their starting and ending locations, the program can estimate how long it would have taken (historically) to get between these locations in the shortest amounts of time, and what types of trips it would take to get them between those two locations. It also produces statistics on the travel times.

TO RUN: Download the project, then create a folder called bus_data, a folder called subway_data, a folder called ferry_data, a folder called trips, and a folder called compiled_data. To bus_data, create a folder for each year you will import data from and download the relevant CSV data from https://mbta-massdot.opendata.arcgis.com/, then put all of the CSV folders corresponding to each year into the respective year folder. Do the same for the subway data. For ferry data, you do not need to create the year folders, but you must rename the file "MBTA_Ferry_Trips.csv". Under compiled_data folder, create an empty folder called events and one called trips. Then, run 04_pipeline.py, input coordinates and time as necessary, and you are good to go.

To change the months that the data runs on, go to the MONTHS list in 01_compile_data.py and 02_find_best_lines.py and add in the lists you want to include for each year. 

Here are some coordinates to help you input into the map:
Cambridge: 

John Harvard Statue: 42.374476, -71.117288

MoFA: 42.338965, -71.093536

Westgate (MIT): 42.354991, -71.102960

MIT Building 7: 42.3590587, -71.0934272

Kendall/MIT - 42.3624332, -71.0853644

Alewife - 42.3960896, -71.1424221

Inman Square - 42.373682, -71.100505



Downtown Boston: 

South Station: 42.352351, -71.054811

North Station / TD Garden: 42.366223, -71.061545

Boston Common Statue - 42.3542693, -71.0655757

Old State House: 42.358867, -71.057481

Prudential Center: 42.346508, -71.082205

Christian Science Plaza: 42.343865, -71.085167

Chinatown Gate: 42.351081, -71.059899

Old North Church: 42.366415, -71.054729

Downtown Crossing: 42.3552056,-71.0604109

Government Center Plaza: 42.360003, -71.059049




Somerville/Chelsea/Everett/Medford (North Side):

Bunker Hill Monument (Charlestown): 42.376177, -71.060655

Consulate of Honduras (Chelsea): 42.394089, -71.041533

Mystic Mall (Chelsea): 42.395857, -71.041453

Bellingham Square (Chelsea): 42.392715, -71.034075

Highland Park (Chelsea): 42.387227, -71.027457

Tufts Tisch Library (Medford): 42.406430, -71.118496

Chevalier Theatre (Downtown Medford): 42.419413, -71.108985

West Medford Commuter Rail Station (Medford): 42.421199, -71.132557

Somerville Theatre (Davis Square, Somerville): 42.396473, -71.122947

Magoun Square (Somerville): 42.397369, -71.104344

Somerville High School (Somerville): 42.386085, -71.095983

MBTA CR Maintainence Facility (Inner Belt, Somerville): 42.376396, -71.076501

Everett Square (Everett): 42.407085, -71.055463

Glendale Park (Everett): 42.413126, -71.045909

MetroRock Climbing (Everett): 42.407089, -71.068184

Encore Hotel (Everett): 42.395635, -71.070567



East Side:

Maverick Square (East Boston) - 42.369598, -71.039223

Central Square East Boston - 42.377140, -71.039546

Lewis Mall (East Boston) - 42.366095, -71.041040

Constitution Beach (Orient Heights)- 42.384857, -71.010409

Madonna, Queen of the Universe Statue (Orient Heights)- 42.390292, -71.005384

Belle Isle Seafood (Winthrop) - 42.382567, -70.993271

Downtown Winthrop (Winthrop) - 42.374750, -70.986272

Revere Beach - 42.4130136, -70.9894010

Deer Island Park - 42.356025, -70.967428

Revere City Hall - 42.408256, -71.013533

Hill Park (Revere) - 42.410662, -71.014548



South Side:

Doughboys Doughnuts and Deli - 42.340355, -71.056828

Rock Spot South Boston - 42.337220, -71.056584

City Point - 42.335443, -71.023654

Dorchester Heights Monument - 42.332834, -71.046034

Boston Design Center (Seaport) - 42.344163, -71.033802

Fan Pier Walkway (Seaport) - 42.354759, -71.046438

Longwood Center (LMA) - 42.338820, -71.107365

BU Medical Campus (SoWA) - 42.334215, -71.072798

Nubian Square - 42.329810, -71.084508

Vine Street Community Center - 42.326959, -71.076446

Uphams Corner - 42.317079, -71.065349

Newmarket Square - 42.327111, -71.067121

Mattapan Square - 42.268620, -71.093726

Hyde Park - 42.255792, -71.124153

Dedham Mall - 42.253007, -71.167420

West Roxbury VA - 42.273860, -71.169809

Newton Centre - 42.329693, -71.192494

Brookline Hills - 42.331495, -71.126449

Brookline Village - 42.332872, -71.118659

Olmstead Park - 42.325353, -71.115280

Franklin Park - 42.303443, -71.085268

Forest Hills - 42.300450, -71.113245

Ruggles - 42.337196, -71.089724

JFK Library - 42.315906, -71.034179



Misc:

Hingham Dock - 42.2523060, -70.9195660 (done best on 2023 data or earlier)

Spicy Hunan Kitchen, Woburn - 42.4804598, -71.1520056

Waltham Square - 42.3751430, -71.2357254
