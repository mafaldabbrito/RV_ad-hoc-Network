#!/usr/bin/env python

#################################################
## GEONETWORK LAYER PROPERTIES
#  Model used: allow packet forwarding according to number of hops and region of interest rules
#################################################

#------------------------------------------------
# forwarding_model = True: allow packet forwarding
#                   False: do not allow packet forwarding
#------------------------------------------------
forwarding_model = False

#------------------------------------------------
# roi_model = True: process packets using the RoI information
#             False: do not allow use RoI information to process the packets
#------------------------------------------------
roi_model  = False

#################################################
## GEONETWORK LAYER EMULATION
#  Model used: do not send data messages, if there are no neighbours (locTable is empty)
#              discard or store packets waiting for valid neighbour to be transmitted
#################################################

#------------------------------------------------
# geonetwork_model = True: forward data messages, if there are valid neighbour
#                    False: alwways send packets
geonetwork_model = False
#------------------------------------------------

#------------------------------------------------
# store_model = True: store messages waiting for transmission
#               False: do not store packets waiting for transmission
#------------------------------------------------
store_model = False


# #####################################################################################################
# LOCATION UPDATE MODEL
# #####################################################################################################
#------------------------------------------------
# Fixed update = True: Fixed increase every time interval.
#                False: Distance update depends on car movement.
#------------------------------------------------
fixed_spaces = 0
delta_space = 10

#################################################
## PHYSICAL LAYER EMULATION
#  Model used: if distance from sender > range, then discard; if  distance from sender in [interference range, range[
#################################################

#------------------------------------------------
# No emulation: accept all packets
physical_model = False
#------------------------------------------------

#------------------------------------------------
# Interference zone limits
#------------------------------------------------
range_scale = 0.8

#------------------------------------------------
# Interference zone packet drop probability
#------------------------------------------------
drop_threshold = 2



rsu_id = 1 # RSU ID (replace with actual ID)


##############################
#  HTTP requests parameters  #
##############################

LOCKED_DEVICES_URL = "http://127.0.0.1:5000/api/locked-devices"  # URL to fetch locked devices
REPORT_THEFT_URL = "http://127.0.0.1:5000/api/report-theft"      # URL to report theft 

GET_URL = "http://193.236.214.159:8080/get_command/1"  # URL to fetch commands 
POST_URL = "http://193.236.214.159:8080/post_command/1"     # URL to send commands


