Required items: 
%%
Raspberry Pi (Any kind)
I2S 3Watt Speaker Bonnet
(2) 3Watt 4Ohm speakers
22-24 AWG threaded wire
_____________
Connect the physical (common sense applies)
%%
# STEP 1
Open "the command prompt" and run 
```
aplay -l
```

You are looking for the PI HAT should look something like "MAX98357A" (there should be 4 cards listed (card 0 is the pi, card 1 and card 2 are the HDMI ports) )
- If it is there move on. [[#STEP 2]]
- If it is not the you need to force it there.
FORCE IT THERE
```
sudo nano /boot/firmware/config.txt
```

go to the bottom of the config and enter 

```
dtparam=audio=on
dtoverlay=max98357a
```

then CTRL+O to write it out
CTRL+X to exit (press y and enter)

If you have successfully added the audio source then
```
sudo reboot
```

When the PI restarts 
```
aplay -l
```
The PI hat should now be there and you can move on.
- if its not ask claude to help you.

# STEP 2

The PI recognizes the audio device so now it's time to test the speakers.
Look at `aplay -l` and write down the card number of your PI HAT. I'm using 3 below, if yours is different swap it out everywhere you see it.
```
speaker-test -D hw:3,0 -c 2 -t sine
```
you should start to see and hear the PI run through a looped speaker test. 
if you do not hear anything start back at [[#STEP 1]]

To stop the test CTRL+c

Now its time to set the audio device as the default audio device.
```
sudo nano /etc/asound.conf
```
here you are creating a configuration file to tell the pi that the default audio device is the specific card.
Enter the below (watch the spelling, "default" has to be spelled right or it gets ignored):
```
pcm.!default {
type plug
slave.pcm "hw:3,0"
}

ctl.!default {
type hw
card 3
}
```
CTRL+O to write it out
CTRL+X to exit then y and enter
if you have successfully written that .conf file reboot
```
sudo reboot
```

when you boot back up make sure it worked. Run the below command without specifying the card to ensure that your default audio device is the PI hat.
```
speaker-test -c 2 -t wav
```
- if it works the CTRL +C to stop the test.
- if it doesn't then return to [[#STEP 2]]
If it still doesn't work then we need to check to make sure your PI is running pipewire appropriately.
```
pactl info | grep "Server Name"
```
then run
```
pactl list short sinks
```
you are looking to make sure that one of the sinks has your audio device listed.

you're looking for the one that looks like "alsa_output.platform-soc_sound.stereo-fallback"
if its there then run the following:
```
pactl set-default-sink alsa_output.platform-soc_sound.stereo-fallback
```
Now set the volume to 50% then incrementally increase it to make sure you don't blow your speakers.
```
pactl set-sink-volume alsa_output.platform-soc_sound.stereo-fallback 50%
```
you can incrementally increase it in the cmd line by hitting the up arrow to get this line back then just change the percentage. 

now open the browser and play some audio.
if you dont have internet then run the following:
```
paplay /usr/share/sounds/alsa/Front_Center.wav
```
double check to make sure your default saved 
```
pactl get-default-sink
```
you should see your audio device "alsa_output.platform-soc_sound.stereo-fallback"
reboot
```
sudo reboot
```
after the reboot then rerun the audio tests. 

# STEP 3
Make the directory or folder that you are going to store your .wav files
```
mkdir -p ~/"TBS Audio"
```
"TBS Audio" is what I am naming my folder you can change that. KEEP THE QUOTES around the name if it has a space in it or the pi will make two separate folders.
THIS FOLDER LIVES IN YOUR HOME FOLDER (~), NOT ON THE DESKTOP. If you save your .wav files in a folder on the desktop the script will not see them.
Your files also need to end in lowercase .wav (sound.wav, not sound.WAV)


now you are going to make the script that auto plays your .wav files a set number of seconds after boot.

first you need to create the .sh file

```
nano ~/play.sh
```

then enter the below:

```
#!/bin/bash
DELAY=1800           # this is the number seconds after boot (1800 = 30 minutes, set to 30 while testing)
DIR="$HOME/TBS Audio" #where you saved the files
SINK="alsa_output.platform-soc_sound.stereo-fallback"

shopt -s nullglob
sleep "$DELAY"

while true; do
    files=("$DIR"/*.wav)
    if [ ${#files[@]} -eq 0 ]; then
        sleep 5
        continue
    fi
    for f in "${files[@]}"; do
        paplay --device="$SINK" "$f" || sleep 5
    done
done
```

Now you need to make this executable.
```
chmod +x ~/play.sh
```
now we need to make the service. The below is going to make the folder and then the config that stores the service.
```
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/audioloop.service
```
When that config is open enter the below:
```
[Unit]
Description=Delayed WAV loop player
After=pipewire.service pipewire-pulse.service

[Service]
ExecStart=%h/play.sh
Restart=always

[Install]
WantedBy=default.target
```

The big part comes now, you don't want to have to have a screen, keyboard, and mouse to run this... You want it to just start after you give the pi its power. So you need some demons to help you with that. 
```
systemctl --user daemon-reload
systemctl --user enable --now audioloop.service
sudo loginctl enable-linger $USER
```
reboot to have that set up
```
sudo reboot
```
when the pi boots back up the process will begin...IF YOU HAVE NOT PUT ANY .wav FILES IN THAT FOLDER... NOTHING WILL PLAY.
(you can add files any time, the script checks the folder again every loop so no restart needed)
but you can still check to make sure the process is still running.
```
journalctl --user -u audioloop -f
```
If you change anything in play.sh later (like the delay) run this so it picks up the change
```
systemctl --user restart audioloop
```
I personally am going to use audacity to record some sounds then transfer them over.