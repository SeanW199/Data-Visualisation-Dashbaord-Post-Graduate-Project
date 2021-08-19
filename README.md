# Data-Visualisation-Dashbaord-Post-Graduate-Project
This my 4th year masters project based around data visualisation Dashboards 

#-#

The aim of this project is to create a data visualisation dashboard for a covid-19 dataset

#-#

When the user first launches the dashabrod they will be met with world map scatter plot. Were they can view the death toll of each country and see where covid is affecting the world more seriously and where it is not.
The is also a line of global totals for deaths, recoveries, active and confirmed cases of covid-19 for the user to view.

Below this is the individual countries data visualisation where the user will be able to select from a dropdown box and select a country to view its data.
This will be in the form of a line graph, pie chart and a list of printed statistics about the selcted countries data.

Below this is the comaprison toolis, this will allow user to select two countries(X1, X2) and select a catergory form the deaths, confirmed, active and recovered (Y) to compare each of the countries by.
Once the user has compared the countries they are able to clcik a link at the bottom of the dashabrod to view the differnet policies that, that country has put in place.

#-#

The dataset the has been used is from the John Hopkins University github linked here: https://github.com/CSSEGISandData/COVID-19
where is is explained further, It contains datasets form various trusted global sources. the datasets cover deaths, confirmed and recovered cases.

#-#

The code for this project is split into 4  sections 

Pandas:
The the first section conatins all the data preperation code which uses pandas to take the datasets and store them in dataframes
The dataframes are combines and add an additional coloumn for the date which is formated to the pandas default
new dataframes are created with reset indexs
A list is also created which conatins the header from all the coloumns

Plotly Express:
Below this section the is a samller sections which was to be dedicated to functions that did not require the callback function
The was only one function created which used the the plotly express library to create the world map visualisation, this was due to the fact the callback functions need
an input but the were no inputs for this visualisations.

#-#

Dash, Dash Bootstrap:
The next section conatins the code responsible layout of the dashabrod and the elements used within them e.g (Pop-outs, dropdown boxes, rows, columns etc.)

Dash:
In the final section is dedicated to the callback functions which are used to dynamically update teh dashabrod when the user makes changes to the layout.
