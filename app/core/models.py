import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, \
                                        PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator

from django.conf import settings
from core import choices


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError()
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User Model to allow email as username"""
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    date_created = models.DateField(auto_now_add=True)
    timezone = models.CharField(
        max_length=50,
        default='Asia/Manila',
        choices=choices.timezone_choices
    )
    is_ntc = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    REQUIRED_FIELDS = ['first_name', 'last_name']

    USERNAME_FIELD = 'email'


class RfcDevice(models.Model):
    """
        Model for the hardware device used by the RFC-6349 test agents
    """
    device_id = models.UUIDField(default=uuid.uuid4, unique=True)
    manufacturer = models.CharField(max_length=250, null=True)
    product = models.CharField(max_length=250, null=True)
    version = models.FloatField(null=True)
    serialnumber = models.CharField(max_length=50, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True,
                                on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    # hash = models.CharField(max_length=64, unique=True, null=False)

    class Meta:
        verbose_name = 'RFC6349 Test Device'
        verbose_name_plural = 'RFC6349 Test Devices'
        ordering = ['-id']


class FieldTester(models.Model):
    """
        Extension of the User model specifically for the test
    clients (aka  Agents)
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    uuid = models.UUIDField(default=uuid.uuid4,
                            editable=False, blank=True, unique=True)
    ntc_region = models.CharField(
        max_length=20, choices=choices.ntc_region_choices,
        default='unknown'
    )
    device_kind = models.CharField(
        max_length=20, choices=choices.device_choices,
        default='computer'
    )
    registration_status = models.CharField(
        max_length=20, choices=choices.registration_choices,
        default='unregistered'
    )
    device = models.ForeignKey(
        RfcDevice,
        null=False,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return "%s" % self.user.username

    def display_name(self):
        if self.user.get_short_name():
            return self.user.get_short_name()
        else:
            return self.user.username


class MobileDevice(models.Model):
    """Android Device assigned to Field Tester"""
    serial_number = models.CharField(max_length=250, null=True, blank=True)
    imei = models.CharField(max_length=250, null=True, blank=True)
    phone_model = models.CharField(max_length=250, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)


class MobileResult(models.Model):
    """Android devices for speed testings"""
    phone_model = models.CharField(max_length=250, null=True, blank=True)
    android_version = models.CharField(max_length=100, null=True, blank=True)
    ssid = models.CharField(max_length=250, null=True, blank=True)
    bssid = models.CharField(max_length=250, null=True, blank=True)
    rssi = models.FloatField(null=True, blank=True)
    network_type = models.CharField(max_length=20, null=True, blank=True)
    imei = models.CharField(max_length=250, null=True, blank=True)
    cellid = models.CharField(max_length=250, null=True, blank=True)
    mcc = models.CharField(max_length=250, null=True, blank=True)
    mnc = models.CharField(max_length=250, null=True, blank=True)
    tac = models.CharField(max_length=250, null=True, blank=True)
    signal_quality = models.CharField(max_length=250, null=True)
    operator = models.CharField(max_length=250, null=True, blank=True)
    lat = models.FloatField(default=0, validators=[MaxValueValidator(90.0),
                            MinValueValidator(-90.0)])
    lon = models.FloatField(default=0, validators=[MaxValueValidator(180.0),
                            MinValueValidator(-180.0)])
    upload = models.FloatField(default=0, null=True, blank=True)
    download = models.FloatField(default=0, null=True, blank=True)
    jitter = models.FloatField(default=0, null=True, blank=True)
    ping = models.FloatField(default=0, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField()
    success = models.BooleanField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)


class IPaddress(models.Model):
    """
        Model for IP addresses containing its geolocation & ISP data
    """
    date = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=False)
    country = models.CharField(max_length=50)
    country_code = models.CharField(max_length=10)
    region = models.CharField(max_length=50)
    region_name = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    pcap = models.CharField(max_length=100, null=True)
    lat = models.FloatField(default=0, validators=[MaxValueValidator(90.0),
                            MinValueValidator(-90.0)])
    lon = models.FloatField(default=0, validators=[MaxValueValidator(180.0),
                            MinValueValidator(-180.0)])
    # lat = models.FloatField(default=0,validators=
    # [MaxValueValidator(90.0), MinValueValidator(-90.0)])
    # long = models.FloatField(default=0, validators=
    # [MaxValueValidator(180.0), MinValueValidator(-180.0)])
    timezone = models.CharField(
        max_length=50, default='Asia/Manila',
        choices=choices.timezone_choices
    )
    isp = models.CharField(max_length=100)
    org = models.CharField(max_length=100)
    as_num = models.CharField(max_length=100)
    as_name = models.CharField(max_length=100)
    reverse = models.CharField(max_length=200)
    mobile = models.BooleanField(default=False)
    proxy = models.BooleanField(default=False)


class Server(models.Model):
    """
        Model for a NetMesh test server
        The same model is used for both RFC-6349 test servers  \
    and Web-based speedtest servers
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    nickname = models.CharField(max_length=200, null=True)
    # assumes that server has a fixed IP address
    ip_address = models.GenericIPAddressField()
    server_type = models.CharField(
        max_length=20,
        choices=choices.server_choices,
        default='unknown'
    )

    lat = models.FloatField(default=0, validators=[MaxValueValidator(90.0),
                            MinValueValidator(-90.0)])
    lon = models.FloatField(default=0, validators=[MaxValueValidator(180.0),
                            MinValueValidator(-180.0)])

    city = models.CharField(
        max_length=200,
        null=True
    )
    province = models.CharField(
        max_length=200,
        null=True
    )
    country = models.CharField(
        max_length=200,
        default='Philippines'
    )
    # organization that hosts this server
    sponsor = models.CharField(
        max_length=200,
        default='SponsorName'
    )
    hostname = models.URLField(
        max_length=500,
        default="https://netmesh-web.asti.dost.gov.ph/"
    )

    def __str__(self):
        return "Server %s (%s)" % (self.nickname, self.uuid)


class Test(models.Model):

    """
        Model to represent results from an RFC-6349 Test
        Each test can contain multiple datapoints
        (i.e. forward, reverse).
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,
        editable=False
    )
    tester = models.ForeignKey(
        FieldTester, null=False,
        on_delete=models.CASCADE
    )
    ip_address = models.ForeignKey(
        IPaddress,
        on_delete=models.CASCADE
    )
    test_type = models.CharField(
        null=False, max_length=50,
        choices=choices.test_type_choices
    )
    date_created = models.DateTimeField(auto_now_add=True)
    network_connection = models.CharField(
        max_length=20,
        null=False,
        default='unknown'
    )
    pcap = models.CharField(max_length=100, null=True)
    lat = models.FloatField(default=0, validators=[MaxValueValidator(90.0),
                            MinValueValidator(-90.0)])
    lon = models.FloatField(default=0, validators=[MaxValueValidator(180.0),
                            MinValueValidator(-180.0)])
    mode = models.CharField(
        null=False, max_length=50,
        choices=choices.test_mode_choices,
        default='unknown'
    )

    def __str__(self):
        return "Test %s" % self.id


class RfcResult(models.Model):
    """
        Model for an RFC-6349 test result
    """

    tester = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    date_tested = models.DateTimeField(
        default=timezone.now
    )
    direction = models.CharField(
        null=False,
        max_length=10,
        choices=choices.direction_choices,
        default='unknown'
    )
    server = models.ForeignKey(
        Server,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    mtu = models.IntegerField(
        null=True,
        blank=True
    )  # Path Max Transmit Unit, in bytes
    rtt = models.FloatField(
        null=True,
        blank=True
    )  # Baseline Round Trip Time, in ms
    bb = models.FloatField(
        null=True,
        blank=True
    )  # Bottleneck Bandwidth, in Mbps
    bdp = models.FloatField(
        null=True,
        blank=True
    )  # Bandwidth Delay Product, in bits
    rwnd = models.FloatField(
        null=True,
        blank=True
    )  # Minimum Receive Window Size, in Kbytes
    thpt_avg = models.FloatField(
        null=True,
        blank=True
    )  # Average TCP Throughput, in Mbps
    thpt_ideal = models.FloatField(
        null=True,
        blank=True
    )  # Ideal TCP throughput, in Mbps
    transfer_avg= models.FloatField(
        null=True,
        blank=True
    )  # Actual Transfer Time, in secs
    transfer_ideal = models.FloatField(
        null=True,
        blank=True
    )  # Ideal Transfer Time, in secs
    tcp_ttr = models.FloatField(
        null=True,
        blank=True
    )  # TCP transfer Time Ratio, unitless
    tx_bytes = models.FloatField(
        null=True,
        blank=True
    )  # Transmitted Bytes, in bytes
    retx_bytes = models.FloatField(
        null=True,
        blank=True
    )  # Retransmitted Bytes, in bytes
    tcp_eff = models.FloatField(
        null=True,
        blank=True
    )  # TCP Efficiency, in %
    ave_rtt = models.FloatField(
        null=True,
        blank=True
    )  # Average Round Trip Time, in ms
    buf_delay = models.FloatField(
        null=True,
        blank=True
    )  # Buffer Delay, in %
    gps_lat = models.FloatField(default=0, validators=[MaxValueValidator(90.0),
                            MinValueValidator(-90.0)])
    gps_lon = models.FloatField(default=0, validators=[MaxValueValidator(90.0),
                            MinValueValidator(-90.0)])
    location = models.CharField(max_length=250, null=True)



class Traceroute(models.Model):
    """
        Model for traceroute information
        Each traceroute can have one or more associated Hops
    """
    date = models.DateTimeField(default=timezone.now)
    origin_ip = models.GenericIPAddressField(null=False)
    dest_ip = models.GenericIPAddressField(null=False)
    dest_name = models.CharField(max_length=200, null=False)


class Hop(models.Model):
    """
        Model for a traceroute Hop
    """
    traceroute = models.ForeignKey(
        Traceroute,
        null=False,
        on_delete=models.CASCADE
    )
    hop_index = models.IntegerField(
        null=False
    )
    time1 = models.FloatField(
        null=True
    )
    time2 = models.FloatField(
        null=True
    )
    time3 = models.FloatField(
        null=True
    )
    host_name = models.CharField(
        max_length=200
    )  # domain name or fallback to IP address if no domain name
    host_ip = models.GenericIPAddressField(
        null=True
    )


class Speedtest(models.Model):
    """
        Model to represent results from a web-based speedtest.
        Note that the web-based speedtest is simpler compared
        to the RFC-6349 result representation
    """
    date = models.DateTimeField(
        default=timezone.now
    )
    test_id = models.UUIDField(
        null=False,
        editable=True,
        unique=True
    )
    sid = models.CharField(
        max_length=32,
        null=False,
        editable=False
    )
    ip_address = models.ForeignKey(
        IPaddress,
        on_delete=models.CASCADE
    )
    server = models.ForeignKey(
        Server,
        on_delete=models.CASCADE
    )
    rtt_ave = models.FloatField(
        null=False
    )
    rtt_min = models.FloatField(
        null=False
    )
    rtt_max = models.FloatField(
        null=False
    )
    upload_speed = models.FloatField(
        null=False
    )
    download_speed = models.FloatField(
        null=False
    )


class NMProDataPoint(models.Model):
    """
        Model for a manually entered NetMaster Pro measurement
    """
    date_created = models.DateTimeField(
        blank=True,
        default=timezone.now
    )
    ip_address = models.GenericIPAddressField(
        null=False,
        verbose_name='Client IP address'
    )
    server = models.GenericIPAddressField(
        null=False,
        verbose_name='Server IP address'
    )
    lat = models.FloatField(default=0, validators=[MaxValueValidator(90.0),
                            MinValueValidator(-90.0)])
    lon = models.FloatField(default=0, validators=[MaxValueValidator(180.0),
                            MinValueValidator(-180.0)])
    mode = models.CharField(
        null=False,
        max_length=10,
        default='unknown',
        choices=[('auto', 'Auto'),
                 ('expert', 'Expert'),
                 ('unknown', 'Unknown')]
    )

    # Test conditions section

    direction = models.CharField(
        null=False,
        max_length=10,
        choices=choices.direction_choices,
        default='unknown'
    )
    min_rwnd = models.FloatField(
        null=True,
        verbose_name='Minimum Receive Window Size',
        help_text='in bytes'
    )
    connections = models.IntegerField(
        null=True,
        verbose_name='Connections',
        help_text='enter number of connections'
    )
    bdp = models.FloatField(
        null=True,
        verbose_name='Bandwidth Delay Product',
        help_text='in bytes'
    )
    path_mtu = models.IntegerField(
        null=True,
        verbose_name='Path MTU',
        help_text='in bytes'
    )
    baseline_rtt = models.FloatField(
        null=True,
        verbose_name='Baseline RTT',
        help_text='in ms'
    )
    cir = models.FloatField(
        null=True,
        verbose_name='CIR',
        help_text='in Mbps'
    )
    bottleneck_bw = models.FloatField(
        null=True,
        verbose_name='Bottleneck Bandwidth',
        help_text='in Mbps'
    )

    # TCP throughput section
    ave_tcp_tput = models.FloatField(
        null=True,
        verbose_name='Average TCP Throughput',
        help_text='in Mbps'
    )
    ideal_tcp_tput = models.FloatField(
        null=True,
        verbose_name='Ideal TCP throughput',
        help_text='in Mbps'
    )
    threshold = models.FloatField(
        null=True,
        verbose_name='Threshold',
        help_text='in %'
    )

    # Transfer Time section
    actual_transfer_time = models.FloatField(
        null=True,
        verbose_name='Actual Transfer Time',
        help_text='in secs'
    )
    ideal_transfer_time = models.FloatField(
        null=True,
        verbose_name='Ideal Transfer Time',
        help_text='in secs'
    )
    tcp_ttr = models.FloatField(
        null=True,
        verbose_name='TCP transfer Time Ratio',
        help_text='unitless'
    )

    # Data Transfer section
    trans_bytes = models.FloatField(
        null=True,
        verbose_name='Transmitted Bytes',
        help_text='in bytes'
    )
    retrans_bytes = models.FloatField(
        null=True,
        verbose_name='Retransmitted Bytes',
        help_text='in bytes'
    )
    tcp_eff = models.FloatField(
        null=True,
        verbose_name='TCP Efficiency',
        help_text='in %'
    )

    # RTT Section
    min_rtt = models.FloatField(
        null=True,
        verbose_name='Minimum Round Trip Time',
        help_text='in ms'
    )
    max_rtt = models.FloatField(
        null=True,
        verbose_name='Maximum Trip Time',
        help_text='in ms'
    )
    ave_rtt = models.FloatField(
        null=True,
        verbose_name='Average Round Trip Time',
        help_text='in ms'
    )
    buffer_delay = models.FloatField(
        null=True,
        verbose_name='Buffer Delay',
        help_text='in %'
    )
