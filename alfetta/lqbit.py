#!/usr/bin/python
import serial, struct, sys, time
import threading

#============================================================================
#---------------------------------------------------------------------------------
class qbit_sensor():
    
    def __init__ (self,dev,pm=25):
        print ("sensor QBit init")
        self.ser = serial.Serial()
        self.ser.port = dev
        self.ser.baudrate = 9600
        self.ser.open()
        self.ser.flushInput()
        self.pm=pm
        self.byte, data = 0, ""
        self.pm10k=1
        self.pm10q=0
        self.pm25k=1
        self.pm25q=0
        self.pm10_acc=0
        self.pm25_acc=0
        self.pm10_act=0
        self.pm25_act=0
#-----------------------------------------------------------
        self.samples=12                 # Numero di campioni per media default
        self.sync=0
        self._pm10_acc=0
        self.pm25_acc=0
        self.sample_number=0
#   print ("Cilco abilitato")
        self.sensor_on=threading.Thread(target=self.__ciclo)
        self.lock=threading.Lock()
        self.sensor_on.start()
        self.status="PAUSE"
#   print ("Init End")

    def get_status(self):
        return(self.status)

    def set_pm10_calibration (self,k,q):
        self.pm10k=k
        self.pm10q=q

    def set_pm25_calibration (self,k,q):
        self.pm25k=k
        self.pm25q=q

    def cmd_query_data(self):
        l={}
        rcv = self.read_response()
        rcv=rcv.replace("\r","")
        if "PM:" in rcv:
#            rcv=rcv.replace("\r","")
#            print ("Primo split:",rcv.split('|'))
            print (time.strftime("%H:%M:%S"),"-----------------------------")
            lrcv=rcv.split("|")
            for e in lrcv:
#                e.replace("\r","")
                val=e.split(":")
                if len(val)==2 :
                    print (val[0],val[1])
                if val[0].replace(" ","") == "PM" :
                    l["pm10"]=val[1]
                    l["pm25"]=val[1]
                    if self.pm==10 :
                        self.pm10=val[1]
                    if self.pm==25 :
                        self.pm25=val[1]
                if val[0].replace(" ","") =="T" :
                    self.t=val[1]
                if val[0].replace(" ","") =="P" :
                    self.p=val[1]
                if val[0].replace(" ","") =="rH" :                  
                    self.rh=val[1]
        else:
            self.pm25=0
            self.pm10=0

    def read_response(self):
        byte = ""
        r=""
        while byte != "\n":
            byte=self.ser.read(1)
            if (byte != "\n" ):
                r=r+byte
#        print "Risposta =",r
        return r

    def cmd_set_sleep(self,sleep=1):
        if sleep == 0 : 
            self.ser.write("stop\n\r")
            self.status="PAUSE"
        else :
            self.ser.write("start\n\r")
            self.status="RUNNING"
        self.read_response()
 
    def set_cicletime(self,runtime):
            runtime=1

    def set_pm10_calib(self,k,q):
        self.pm10k=k
        self.pm10q=q
            
    def set_pm25_calib(self,k,q):
        self.pm25k=k
        self.pm25q=q
            
    def elaborate (self):
#        print "elabora ",self.pm25,self.pm25k,self.pm25q,self.samples
        if self.pm==10 :
            self.pm10_acc=self.pm10_acc+(self.pm10k*int(self.pm10)+self.pm10q)/float(self.samples)
        if self.pm==25 :
            self.pm25_acc=self.pm25_acc+(self.pm25k*int(self.pm25)+self.pm25q)/float(self.samples)
#        print "pm25 acc = ",self.pm25_acc
    def measure(self,op):
        try:
            self.lock.acquire()
            if op=="update" :
                self.update_measure()
            if  op =="get":
                return(self.get_measure())
        finally:
            self.lock.release()
 
    def update_measure(self):
        self.pm10_act = self.pm10_acc
        self.pm25_act = self.pm25_acc
        self.t_act=self.t
        self.p_act=self.p
        self.rh_act=self.rh 
        self.validate=True
        print (self.pm10_act,self.pm25_act)
        self.pm10_acc=0
        self.pm25_acc=0  
        
    def get_measure(self):
        pm10_tmp=self.pm10_act
        pm25_tmp=self.pm25_act
        return (pm10_tmp,pm25_tmp,self.validate)

    def stop_ciclo(self):
        self.sensor_on.do_run=False
        self.sensor_on.join()
        return(True)
            
    def __ciclo(self):
        self.validate = False
        self.cmd_set_sleep(1);
        time.sleep(3)
        t=threading.currentThread()
        while getattr(t,"do_run",True):
            Tmedia=self.samples
            for i in range (1,Tmedia+1):
                inizio=time.time()
                self.cmd_query_data();
                self.elaborate()             # esegue per ora solo la media 
                self.sample_number=i
                fine=time.time()
#               print ("Durata", fine-inizio)
#                   time.sleep(1)
            self.measure("update")
        self.cmd_set_sleep(0)
        print ("STOP\n")
        self.ser.close()
#------------------------------------------------------------------------------


