# chip_axp209_tool
Python script to query 9$ Chip's I2C module AXP209

## Need for this module
I wanted to monitor my chip's battery health & status by calling i2c module in 9$ chip's axp209 IC in a loop. By default 9$ chip comes
with a shell script named **axp209** . This tool internally use **i2c-tools** package **i2cget** command, **bc** command and **bash**
to get the values.

To fetch most of the value in **axp209** script, Chip's linux executes **almost 57 commands** !!

As I am going to run a program in daemon mode and consuming little CPU/battery resources, I looked for python module smbus.
But smbus module does not allow to open the i2c-device during call to set **SMBus_set_addr** call in py-smbus/smbusmodule.c 
from i2c-tools source code at [Modified i2c-tools](https://github.com/GssMahadevan/i2c-tools).  
I tried to update latest i2c-tools 3.1.1, but couldn't find any gitbub at lm-sensors.org. So I forked the code from 
[groeck/i2c-tools](https://github.com/groeck/i2c-tools).


In C program **i2cget**, there is an option to open forcefully (by knowing the danegerous consequences). Such option is provided
in smbus module in [Modified i2c-tools/py-smbus](https://github.com/GssMahadevan/i2c-tools/py-smbus/)

Only three lines were changed. No interfaces or methods were added. Used OS-environment variables to allow forcefull opening (though
not the best way). To allow forceful opening user needs to provide command line option **-F**.

## Pre Requisitives
Ensure that you have enhanced i2c-tools/py-smbus module from above links
## Usage of chip_axp209_tool
####To collect most of the values as in axp209 script with time,mac, name , value and units
```
/opt/bin/axp209.py  -F  -TNDU  -taAcdvfsbpzZr   
```
Output looks like:
```
Sun Aug 14 18:02:54 2016 cc79cf23e973         temperature               50.5 oC        
Sun Aug 14 18:02:54 2016 cc79cf23e973         ac_voltage                 0.0 mV        
Sun Aug 14 18:02:54 2016 cc79cf23e973         vbus_power               0x03           
Sun Aug 14 18:02:54 2016 cc79cf23e973         fuel_gauge               0x64           
Sun Aug 14 18:02:54 2016 cc79cf23e973         shutdown_voltage         0x00           
Sun Aug 14 18:02:54 2016 cc79cf23e973         ac_current                 0.00 mA        
Sun Aug 14 18:02:54 2016 cc79cf23e973         battery_voltage          4171.20 mV        
Sun Aug 14 18:02:54 2016 cc79cf23e973         charge_current             0.00 mA        
Sun Aug 14 18:02:54 2016 cc79cf23e973         dicharge_current           0.00 mA        
Sun Aug 14 18:02:54 2016 cc79cf23e973         ac_present               0x00           
Sun Aug 14 18:02:54 2016 cc79cf23e973         reg_0x00_bit2            0x00           
Sun Aug 14 18:02:54 2016 cc79cf23e973         battery_charging         0x00           
Sun Aug 14 18:02:54 2016 cc79cf23e973         battery_connected        0x01 
```

####To get in succinct format without time and mac address
```
/opt/bin/axp209.py  -F    -NU  -tfbcdzZ
```

Output looks like:
```
 temperature               50.5 oC        
 fuel_gauge               0x64           
 battery_voltage          4171.20 mV        
 charge_current             0.00 mA        
 dicharge_current           0.00 mA        
 battery_charging         0x00           
 battery_connected        0x01   
```

####To get the above values with time in infinite loop with 60 seconds sleep in between (for data collection in daemon mode) with comma seperated values
**Hint:** Set loops as 0 to get infinite value. By default only one loop would be executed.
```
/opt/bin/axp209.py  -F    -NT  -tfbcdzZ -l 0 -w 60 -C
```
Output looks like:
``` 
Sun Aug 14 18:17:49 2016,temperature             , 48.9
Sun Aug 14 18:17:49 2016,fuel_gauge              ,0x64
Sun Aug 14 18:17:49 2016,battery_voltage         ,4171.20
Sun Aug 14 18:17:49 2016,charge_current          ,  0.00
Sun Aug 14 18:17:49 2016,dicharge_current        ,  0.00
Sun Aug 14 18:17:49 2016,battery_charging        ,0x00
Sun Aug 14 18:17:49 2016,battery_connected       ,0x01
Sun Aug 14 18:18:49 2016,temperature             , 47.3
Sun Aug 14 18:18:49 2016,fuel_gauge              ,0x64
Sun Aug 14 18:18:49 2016,battery_voltage         ,4171.20
Sun Aug 14 18:18:49 2016,charge_current          ,  0.00
Sun Aug 14 18:18:49 2016,dicharge_current        ,  0.00
Sun Aug 14 18:18:49 2016,battery_charging        ,0x00
Sun Aug 14 18:18:49 2016,battery_connected       ,0x01
```


