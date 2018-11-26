# postgres stuff.
'''
DROP TABLE IF EXISTS gtfs_rt;

CREATE TABLE gtfs_rt(
    id SERIAL PRIMARY KEY,
    arrival_delay INTEGER,
    arrival_time TIMESTAMP without time zone,
    arrival_uncertainty SMALLINT,
    departure_delay INTEGER,
    departure_time TIMESTAMP without time zone,
    departure_uncertainty SMALLINT,
    stop_id VARCHAR (4),
    stop_sequence SMALLINT,
    trip_id VARCHAR (20),
    scrape_time TIMESTAMP without time zone
)
'''


import requests, json

# this is the default key they offer to the public.
api_key = 'MW9S-E7SL-26DU-VV8V'

#############################
# Effectively,  We have access to the route schedules; what time we would EXPECT trains to depart.
#  We Also Can peek at every stations' signs for the next few coming trains for every route.
#  Perhaps the best way to collect data is to take peeks at a regular interval around the average
#     Stop to stop travel time,  and measure lateness that way.
#  One big issue is that we are really only looking at ONE feature: lateness.
##############################

# gtfs api request. should pull without ascii, going to need to transform it somehow
# https://groups.google.com/forum/#!topic/bart-developers/w715p0WxSSs
'http://api.bart.gov/gtfsrt/tripupdate.aspx?ascii=y'
'''
header {
    gtfs_realtime_version: "1.0"
    incrementality: FULL_DATASET timestamp: 1542313851
}
entity {
    id: "1011230WKDY"
    trip_update {
        trip {
            trip_id: "1011230WKDY"
        }
        stop_time_update {
            stop_sequence: 1 arrival {
                delay: 36 time: 1542313541 uncertainty: 30
            }
            departure {
                delay: 36 time: 1542313565 uncertainty: 30
            }
            stop_id: "WARM"
        }
        stop_time_update {
            stop_sequence: 2 arrival {
                delay: 33 time: 1542314234 uncertainty: 30
            }
            departure {
                delay: 33 time: 1542314258 uncertainty: 30
            }
            stop_id: "FRMT"
'''
# request.elapsed == response time.
# count for trains in the system
requests.get('https://api.bart.gov/api/bsa.aspx?cmd=count&key=MW9S-E7SL-26DU-VV8V&json=y')

# Get what route schedule is in effect
requests.get('https://api.bart.gov/api/sched.aspx?cmd=scheds&key=MW9S-E7SL-26DU-VV8V&json=y')

# get what that route schedule is (for route 11)
requests.get('https://api.bart.gov/api/sched.aspx?cmd=routesched&route=11&key=MW9S-E7SL-26DU-VV8V&time=12:47+am&json=y')
#  posssible routs are 1-8, 11-12 and 19-20
# dict['root']['route']
'''  
@trainId: "5030513",
    @trainIdx: "5",
    @index: "5",
    stop: [
        {
        @station: "DUBL",
        @load: "1",
        @level: "normal",
        @origTime: "5:13 AM",
        @bikeflag: "1",
    },...
'''
# this is for the etd
requests.get('https://api.bart.gov/api/etd.aspx?cmd=etd&orig=ALL&key=MW9S-E7SL-26DU-VV8V&json=y')
# returns this in dict['root']['station']
'''{u'destination': u'Millbrae',
    u'abbr': u'MLBR',
    u'etd': [{u'abbreviation': u'RICH',
      u'destination': u'Richmond',
      u'estimate': [{u'bikeflag': u'1',
        u'color': u'RED',
        u'delay': u'0',
        u'direction': u'North',
        u'hexcolor': u'#ff0000',
        u'length': u'4',
        u'minutes': u'Leaving',
        u'platform': u'3'},
       {u'bikeflag': u'1',
        u'color': u'RED',
        u'delay': u'0',
        u'direction': u'North',
        u'hexcolor': u'#ff0000',
        u'length': u'5',
        u'minutes': u'20',
        u'platform': u'3'},
       {u'bikeflag': u'1',
        u'color': u'RED',
        u'delay': u'0',
        u'direction': u'North',
        u'hexcolor': u'#ff0000',
        u'length': u'5',
        u'minutes': u'35',
        u'platform': u'3'}],
      u'limited': u'0'}]'''


from google.protobuf.internal.decoder import _DecodeVarint32
import gtfs_realtime_pb2

# Google GTFS-rt proto: https://developers.google.com/transit/gtfs-realtime/gtfs-realtime-proto

proto = gtfs_realtime_pb2

with open("bintest.pb", "rb") as f:
    data = f.read() # read file as string
decoder = _DecodeVarint32

next_pos, pos = 0, 0
while pos < len(data):
    msg = proto.FeedMessage()                    # your message type
    next_pos, pos = decoder(data, pos)
    msg.ParseFromString(data[pos:pos + next_pos])
    # use parsed message

    pos += next_pos
print "done!"
