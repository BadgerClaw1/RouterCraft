# RouterCraft
Run a minecraft server on the TEMU router!

NOTE: BareIronOperator only runs on UNIX terminals. It does not work on WSL due to the way networking works.

Instructions:

Server Operator (NOTE: Run all commands without quotations):
1. Run "sudo apt-get install python3 wget telnet" (Or your distribution's equivalent) 
2. Run "git clone https://github.com/BadgerClaw1/RouterCraft.git && cd RouterCraft/"
3. Connect to the Wi-Fi Repeater
4. Run the command "ip a" in your terminal. Make note of your computer's new IP from the router. It should be in the format 192.168.11.???
5. Run "nano BareIronOperator.py". Edit DEVICE_IP to the ip from instruction #4. Then, type Ctrl+X then y then enter
6. python3 BareIronOperator.py
7. Press 1 then Enter to gain initial access to the router
8. Press 2 then Enter to start the server
9. Start Minecraft 1.21.8 client using the Minecraft Launcher (or a custom launcher with no mods)
10. Click on Mulitplayer, then Direct Connection, then type 192.168.11.1:25565
11. Once you're done playing Minecraft, type 3 then press Enter on the BareIronOperator script to stop the server and back up the world.

Hardware:

These models are confirmed working:

https://www.aliexpress.us/item/3256809291228259.html?spm=a2g0o.order_list.order_list_main.39.369818021M5sOk&gatewayAdapt=glo2usa
https://www.aliexpress.us/item/3256808325746339.html?spm=a2g0o.order_list.order_list_main.44.369818021M5sOk&gatewayAdapt=glo2usa

Credits:

Video the original exploit was taken from: https://www.youtube.com/watch?v=KsiuA5gOl1o
BareIron Minecraft Server source code: https://github.com/p2r3/bareiron
