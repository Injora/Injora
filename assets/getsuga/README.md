# Getsuga Tenshō banner

`ichigo-getsuga.gif` is shown at the top of the "🌙 Getsuga Tenshō" section of the
profile README.

Source: a clip from *Bleach: Hell Verse* (2010), as hosted on Tenor
(https://tenor.com/view/ichigo-kurosaki-getsuga-tensho-visored-hell-verse-bleach-gif-23887237).
Bleach © Tite Kubo / Shueisha / Studio Pierrot. Used here as non-commercial fan
content; it will be removed on request from the rights holder.

Processing (source kept out of git in `assets/source/`):

```sh
VF="trim=start=0:end=3.08,setpts=PTS-STARTPTS,hflip,crop=640:200:0:45,scale=960:300:flags=lanczos,fps=24"
ffmpeg -i getsuga-source.mp4 -vf "${VF},palettegen=max_colors=128:stats_mode=diff" palette.png
ffmpeg -i getsuga-source.mp4 -i palette.png \
  -lavfi "${VF}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" -loop 0 raw.gif
gifsicle -O3 --lossy=40 raw.gif -o ichigo-getsuga.gif
```
