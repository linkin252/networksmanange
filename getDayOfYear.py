import datetime

def countDay_1OfYear(now):
    dayCount = now - datetime.date(now.year - 1, 12, 31)  # 减去上一年最后一天
    if dayCount.days == 1:
        dayCount = countDay_1OfYear(datetime.date(now.year-1,12,31))
    elif dayCount.days == 365 or dayCount.days == 366:
        return dayCount
    else:
        return dayCount.days - 1
    return dayCount.days
    # print('%s是%s年的第%s天。' % (now, now.year, dayCount.days))

dayCount = countDay_1OfYear(datetime.date.today())
print(dayCount)