# set up the packages we need

package { 'nginx':
      ensure => present,
      before => File['/etc/nginx/conf.d'],
}

package { 'git':
     ensure => present
}

exec { "/opt/OhHo4oop-ec2autoscale/scripts/install-server.sh" 
     creates => "/etc/nginx/sites-enabled/kooaba-worker"

}


exec { "