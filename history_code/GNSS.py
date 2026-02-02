import pynmea2
import serial.tools.list_ports


def DaysOfTheMonth(year, month):
    Feb = 28
    if year % 4 == 0 and year % 100 != 0:
        Feb = 29
    elif year % 400 == 0:
        Feb = 29
    elif year % 3200 == 0 and year % 172800 == 0:
        Feb = 29
    if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
        return 31
    elif month == 4 or month == 6 or month == 9 or month == 11:
        return 30
    else:
        return Feb


def UTCtoG8(UTC_time, UTC_date):
    hour = UTC_time.hour
    minute = UTC_time.minute
    second = UTC_time.second
    year = UTC_date.year
    month = UTC_date.month
    day = UTC_date.day

    hour = hour + 8
    if hour > 23:
        hour = hour - 24
        day = day + 1

    if day > DaysOfTheMonth(year, month):
        day = day - DaysOfTheMonth(year, month)
        month = month + 1

    if month > 12:
        year = year + 1
        month = month - 12

    return year, month, day, hour, minute, second


def position_get(GPGGA, GPRMC):
    GGA = pynmea2.parse(GPGGA)
    RMC = pynmea2.parse(GPRMC)

    loc_status = RMC.status  # 定位状态
    loc_mode = RMC.mode_indicator  # 定位模式
    date_UTC = RMC.datestamp  # UTC日期
    time_UTC = RMC.timestamp  # UTC时间
    longitude = RMC.longitude  # 经度
    latitude = RMC.latitude  # 纬度
    longitude_hemisphere = RMC.lon_dir  # 经度半球
    latitude_hemisphere = RMC.lat_dir  # 纬度半球
    velocity = RMC.spd_over_grnd * 1.852  # 速度
    altitude = GGA.altitude  # 海拔高度
    direction = RMC.true_course  # 航向

    year, month, day, hour, minute, second = UTCtoG8(time_UTC, date_UTC)

    if longitude_hemisphere == 'W':
        longitude_hemisphere = '西经'
    elif longitude_hemisphere == 'E':
        longitude_hemisphere = '东经'
    if latitude_hemisphere == 'N':
        latitude_hemisphere = '北纬'
    elif latitude_hemisphere == 'S':
        latitude_hemisphere = '南纬'

    std_inf = (
        loc_status, loc_mode, date_UTC, time_UTC, longitude, latitude, longitude_hemisphere, latitude_hemisphere,
        velocity,
        altitude, direction)
    G8_time = (year, month, day, hour, minute, second)

    return std_inf, G8_time


def print_result(res):
    (std_inf, G8_time) = res
    (loc_status, loc_mode, date_UTC, time_UTC, longitude, latitude, longitude_hemisphere, latitude_hemisphere, velocity,
     altitude, direction) = std_inf
    (year, month, day, hour, minute, second) = G8_time

    if loc_status == 'A':
        str_A = '当前状态：定位有效（A）'
    elif loc_status == 'V':
        str_A = '当前状态：定位无效（V）'

    if loc_mode == 'A':
        str_B = str_A + ' 自主定位（A）'
    elif loc_mode == 'D':
        str_B = str_A + ' 差分（D）'
    elif loc_mode == 'E':
        str_B = str_A + ' 估算（E）'
    elif loc_mode == 'N':
        str_B = str_A + ' 数据无效（N）'

    if loc_status != 'V' and loc_mode != 'N':
        str_C = '当前时间：' + str(year).zfill(4) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2) + ' ' + str(
            hour).zfill(2) + ':' + str(minute).zfill(2) + ':' + str(second).zfill(2)
        str_D = '当前位置：' + latitude_hemisphere + '{:.6f}'.format(
            latitude) + '度 ' + longitude_hemisphere + '{:.6f}'.format(longitude) + '度'
        str_E = '当前速度：' + '{:.3f}'.format(velocity) + ' km/h'
        str_F = '当前海拔高度：' + str(altitude)
        str_G = '当前方向：' + str(direction) + '° （0°为北，顺时针方向）'
        str_ALL = str_B + '\n' + str_C + '\n' + str_D + '\n' + str_E + '\n' + str_F + '\n' + str_G
    else:
        str_ALL = '未定位！'

    return str_ALL,str_C,str_D,str_E,str_F,str_G

if __name__ == '__main__':
    # print(GGA.data)
    # print(GGA.name_to_idx)
    # print(RMC.data)
    # print(RMC.name_to_idx)

    flag = 0

    # 打开 COM17，将波特率配置为115200，数据位为8，停止位为2，无校验位，读超时时间为0.5秒
    ser = serial.Serial(port="COM8",
                        baudrate=115200,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_TWO,
                        timeout=0.5)

    if ser.isOpen():  # 判断串口是否成功打开
        print("打开串口" + str(ser.name) + "成功。")
    else:
        print("打开串口失败。")

    # 读取串口输入信息并输出
    while True:
        inf = ser.readline()
        if inf.endswith(b'\r\n'):
            line = str(inf, "ascii")
            if line.startswith('$GPGGA'):
                loc_GGA = line
                flag = flag + 1
            elif line.startswith('$GPRMC') and flag == 1:
                loc_RMC = line
                flag = flag + 1
            if flag == 2:
                print('------------GPS Positioning Information------------')
                print(print_result(position_get(loc_GGA, loc_RMC)), end='\n')
                print('------------------------End------------------------')
                flag = 0
        else:
            continue
