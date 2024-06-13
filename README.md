## openplotter-dashboards

OpenPltter app to manage dashboards. 

### Installing

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **production**.

#### For production

Install Dashboards from openplotter-settings app.

#### For development

Install dependencies:

`sudo apt install openplotter-settings openplotter-signalk-installer`

Clone the repository:

`git clone https://github.com/openplotter/openplotter-dashboards`

Make your changes and create the package:

```
cd openplotter-dashboards
dpkg-buildpackage -b
```

Install the package:

```
cd ..
sudo dpkg -i openplotter-dashboards_x.x.x-xxx_all.deb
```

Run:

`openplotter-dashboards`

Pull request your changes to github and we will check and add them to the next version of the [Debian package](https://cloudsmith.io/~openplotter/repos/openplotter/packages/).

### Documentation

https://openplotter.readthedocs.io

### Support

http://forum.openmarine.net/forumdisplay.php?fid=1
