## To run the python script at the system boot, follow below steps

 1. Create a new service                                                                                                                                                
	 `sudo vi /lib/systemd/system/sfe_websocket_service.service`
 2. Add below content to the file and edit accoriding to the python script
	> [Unit]                                                                                                                                                        
Description=Sensor Fusion Evaluation Websocket Server                                                                                                                   
After=network.target                                                                                                                                                    
[Service]                                                                                                                                                               
Type=idle                                                                                                                                                               
Restart=on-failure                                                                                                                                                      
User=root                                                                                                                                                               
ExecStart=/bin/bash -c 'cd /home/root/sfe/ && python3 app.py'                                                                                                           
[Install]                                                                                                                                                               
WantedBy=multi-user.target                                                                                                                                              
 3. Set permission for the service file                                                                                                                                 
`sudo chmod 644 /lib/systemd/system/sfe_websocket_service.service`
 4. Configure systemd                                                                                                                                                   
 `sudo systemctl daemon-reload`                                                                                                                                         
 `sudo systemctl enable sfe_websocket_service.service`
 5. Start service                                                                                                                                                       
 `sudo systemctl start sfe_websocket_service.service`                                                                                                                   
 `sudo systemctl start sfe_websocket_service`
 
 
#### Refer [this link](https://www.codementor.io/@ufukafak/how-to-run-a-python-script-in-linux-with-systemd-1nh2x3hi0e)  for more details

*We can create as many services to run different python scripts*
