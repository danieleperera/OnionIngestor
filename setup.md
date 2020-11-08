# Install following docker images
### splash javascript render browser
>sudo docker pull scrapinghub/splash

>sudo docker run -d -p 8050:8050 --net="host" scrapinghub/splash

```
sudo docker run -it -p 8050:8050 --net="host" \
      -v /home/<USER>/splash/proxy-profiles:/etc/splash/proxy-profiles \
      -v /home/<USER>/splash/js-profiles:/etc/splash/js-profiles \
      scrapinghub/splash \
      -v2
```

### alpine-tor image Lots of IP addresses. One single endpoint for your client. Load-balancing by HAproxy.
>sudo docker pull zeta0/alpine-tor:latest

>sudo docker run -d -p 5566:5566 -p 2090:2090 -e tors=5 zeta0/alpine-tor

#### create file in /home/<USER>/splash/proxy-profiles/default.ini
```
>>>
[proxy]
host=localhost
port=9050
type=SOCKS5
<<<
```

#### Tests
>wget 'http://localhost:8050/render.png?url=http://ifconfig.me' -O test_ifconfig.png

>wget 'http://localhost:8050/render.png?url=http://archivecaslytosk.onion/' -O test_onion.png

>curl -x socks5h://localhost:5566 http://archivecaslytosk.onion/

** Fix for issue proxy not working **
https://github.com/scrapinghub/splash/issues/268

### Docker useful commands
>docker ps -aq
>docker stop $(docker ps -aq)
>docker rm $(docker ps -aq)
>docker rmi $(docker images -q)



