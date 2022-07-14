import pickle
from datetime import datetime, timedelta
from apiclient import discovery
from work import working_folder

def fain_free_time(service,calendar_id,i):
    new_day = datetime.now() + timedelta(days=+i)
    list_free_time = new_day.strftime("%d.%m.%Y")+"\n"
    timeMin = new_day.strftime("%Y-%m-%dT00:00:00+03:00")
    timeMax = new_day.strftime("%Y-%m-%dT23:59:59+03:00")
    result = service.events().list(calendarId=calendar_id,
                                   timeZone="Europe/Moscow",
                                   singleEvents=True,
                                   orderBy="startTime",
                                   timeMin=timeMin,
                                   timeMax=timeMax).execute()
    start_time = '08:00:00'
    end_time = '23:59:59'
    if result['items'] != []:
        for i in range(len(result['items'])):
            if 'start' in result['items'][i]:
                date_start = str(result['items'][i]['start']['dateTime'])[:19].split("T")[1]
                date_end = str(result['items'][i]['end']['dateTime'])[:19].split("T")[1]
                #print(f"{date_start} >= {start_time}")
                if date_start >= start_time:
                    if date_start > start_time:
                        free_time = str(datetime.strptime(date_start, "%H:%M:%S") - datetime.strptime(start_time, "%H:%M:%S")).split(":")
                        if int(free_time[0]) > 0 or int(free_time[1]) >= 30:
                            print(f"свободное время с {start_time[:5]} по {date_start[:5]} - {free_time[0]}ч.{free_time[1]}мин.")
                            list_free_time += f"свободное время с {start_time[:5]} по {date_start[:5]} - {free_time[0]}ч.{free_time[1]}мин.\n"
                        start_time = date_end
                    else:
                        start_time = date_end
                elif date_start <= start_time:
                    if date_end > start_time:
                        start_time = date_end
                if len(result['items'])-1 == i:
                    if date_end < start_time:
                        free_time = str(datetime.strptime(end_time, "%H:%M:%S") - datetime.strptime(start_time,"%H:%M:%S")).split(":")
                        print(f"свободное время с {start_time[:5]} по {end_time[:5]} - {free_time[0]}ч.{free_time[1]}мин.")
                        list_free_time += f"свободное время с {start_time[:5]} по {end_time[:5]} - {free_time[0]}ч.{free_time[1]}мин.\n"
                    else:
                        free_time = str(datetime.strptime(end_time, "%H:%M:%S") - datetime.strptime(date_end,"%H:%M:%S")).split(":")
                        print(f"свободное время с {date_end[:5]} по {end_time[:5]} - {free_time[0]}ч.{free_time[1]}мин.")
                        list_free_time += f"свободное время с {date_end[:5]} по {end_time[:5]} - {free_time[0]}ч.{free_time[1]}мин.\n"
    else:
        free_time = str(datetime.strptime(end_time, "%H:%M:%S") - datetime.strptime(start_time, "%H:%M:%S")).split(":")
        print(f"свободное время с {start_time[:5]} по {end_time[:5]} - {free_time[0]}ч.{free_time[1]}мин.")
        list_free_time += f"свободное время с {start_time[:5]} по {end_time[:5]} - {free_time[0]}ч.{free_time[1]}мин.\n"
    return list_free_time

def fain_free_time_numeric(service,calendar_id,i):
    new_day = datetime.now() + timedelta(days=+i)
    list_free_time = 0
    print("***", list_free_time, "***")
    print(new_day)
    timeMin = new_day.strftime("%Y-%m-%dT00:00:00+03:00")
    timeMax = new_day.strftime("%Y-%m-%dT23:59:59+03:00")
    result = service.events().list(calendarId=calendar_id,
                                   timeZone="Europe/Moscow",
                                   singleEvents=True,
                                   orderBy="startTime",
                                   timeMin=timeMin,
                                   timeMax=timeMax).execute()
    start_time = '08:00:00'
    end_time = '23:59:59'
    if result['items'] != []:
        for i in range(len(result['items'])):
            if 'start' in result['items'][i]:
                date_start = str(result['items'][i]['start']['dateTime'])[:19].split("T")[1]
                date_end = str(result['items'][i]['end']['dateTime'])[:19].split("T")[1]

                if date_start >= start_time:
                    if date_start > start_time:
                        print('(', start_time, '-', end_time, ')', i)
                        print(date_start, date_end, i)
                        free_time = str(datetime.strptime(date_start, "%H:%M:%S") - datetime.strptime(start_time, "%H:%M:%S")).split(":")
                        print(free_time, "free_time")
                        if int(free_time[0]) > 0 or int(free_time[1]) >= 30:
                            list_free_time += (((int(free_time[0]) * 60) + int(free_time[1])) // 30) * 5
                            print("***", (((int(free_time[0]) * 60) + int(free_time[1])) // 30) * 5, "***")
                            print("$***$", list_free_time, "$***$")
                        start_time = date_end
                    else:
                        start_time = date_end
                elif date_end > start_time:
                        start_time = date_end
                if len(result['items'])-1 == i: # определяем последнюю задачу, если общеее количество = счетчику то оно последнее, финал
                    # print(date_end, start_time)
                    print("***", list_free_time, "***")
                    if date_end < start_time:
                        free_time = str(datetime.strptime(end_time, "%H:%M:%S") - datetime.strptime(start_time,"%H:%M:%S")).split(":")
                        list_free_time += ((int(free_time[0]) * 60) + int(free_time[1])) // 30 * 5
                    else:
                        print(end_time, date_end)
                        if str(end_time) != '23:59:59' and str(date_end) != '00:00:00':
                            free_time = str(datetime.strptime(end_time, "%H:%M:%S") - datetime.strptime(date_end,"%H:%M:%S")).split(":")
                            print(free_time, "free_time")
                            list_free_time += ((int(free_time[0]) * 60) + int(free_time[1])) // 30 * 5
                        else:
                            print(list_free_time, "***")
    else:
        free_time = str(datetime.strptime(end_time, "%H:%M:%S") - datetime.strptime(start_time, "%H:%M:%S")).split(":")
        list_free_time += ((int(free_time[0]) * 60) + int(free_time[1])) // 30 * 5
    if list_free_time > 50:
        list_free_time = 50
    if list_free_time < 5:
        list_free_time = 5
    return list_free_time

def free_time(name,ru_name,week):
    credentials = pickle.load(open(f"{working_folder}calendar_tokens/token_{name}.pkl", "rb"))
    service = discovery.build("calendar", "v3", credentials=credentials, cache_discovery=False)
    ################## Get My Calendars ###################
    result = service.calendarList().list().execute()
    ##################### Get My Calendar Events #####################
    calendar_id = result['items'][0]['id']
    if week:
        day = 7
    else:
        day = 1

    print(ru_name)
    list_free_time = str(ru_name) + "\n"
    for i in range(day):
        list_free_time += fain_free_time(service, calendar_id, i)
    return list_free_time

def tomorrow(name,num=False,day=1):
    credentials = pickle.load(open(f"{working_folder}calendar_tokens/token_{name}.pkl", "rb"))
    service = discovery.build("calendar", "v3", credentials=credentials, cache_discovery=False)
    ################## Get My Calendars ###################
    result = service.calendarList().list().execute()
    ##################### Get My Calendar Events #####################
    calendar_id = result['items'][0]['id']
    if int(datetime.now().strftime("%H")) <= 6 and day == 0:
        day -= 1
    if num:
        if name != 'Leila':
            list_free_time = fain_free_time_numeric(service, calendar_id,day)
        else:
            list_free_time = int(fain_free_time_numeric(service, calendar_id, day) * 0.6)
    else:
        list_free_time = fain_free_time(service, calendar_id, day)
    if num and (int(datetime.now().strftime('%w')) == 0 or int(datetime.now().strftime('%w')) == 1) and day == -1:
        return list_free_time/2
    else:
        return list_free_time



if __name__ == "__main__":
    tomorrow("Vova",True,-1)