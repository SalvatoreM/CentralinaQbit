# CentralinaQbit
Installare i seguenti servizi e librerie che servono al python della centralina e al codice PHP per la pagina Web 
di configurazione :
ntpd per sincronizzazione data-orologio
- Apache2 – PHP – libapche2.. (https://www.raspberrypi.org/documentation/remote-access/web-server/apache.md)
- python-serial con apt-get
- curl
- INCRON (apt-get) (inotify)
   '# <path> <mask> <command>
configurare incron con

 #sudo incrontab -e
 
 editare la seguente riga 
 
 /var/www/html/alfetta/comandi/ IN_CLOSE_WRITE $@/$#
 
 chiudere l'editor
  
 
