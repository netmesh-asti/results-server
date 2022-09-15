import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, \
                                        PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator

from django.conf import settings

from durin.models import Client

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
    ntc_region = models.CharField(
        max_length=20, choices=choices.ntc_region_choices,
        default='unknown'
    )
    timezone = models.CharField(
        max_length=50,
        default='Asia/Manila',
        choices=choices.timezone_choices
    )
    is_ntc = models.BooleanField(default=True)
    is_field_tester = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    REQUIRED_FIELDS = ['first_name', 'last_name']

    USERNAME_FIELD = 'email'


class RfcDevice(models.Model):
    """
        Model for the hardware (pc/laptop) device used
        by the RFC-6349 test agents
    """
    client = models.OneToOneField(Client, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    name = models.CharField(max_length=250, null=False)
    manufacturer = models.CharField(max_length=250, blank=True)
    product = models.CharField(max_length=250, blank=True)
    version = models.CharField(max_length=250, blank=True)
    serial_number = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    kernel = models.CharField(max_length=50, blank=True)
    ram = models.CharField(max_length=50, blank=True)
    disk = models.CharField(max_length=50, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'RFC6349 Test Device'
        verbose_name_plural = 'RFC6349 Test Devices'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=[
                'user', 'serial_number', 'name'],
                name="unique rfc device")
            ]

    def __str__(self):
        return f"{self.user.email}<{self.serial_number}>"


class MobileDevice(models.Model):
    """Android Device assigned to Field Tester"""
    client = models.OneToOneField(Client, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=250, blank=True)
    imei = models.CharField(max_length=250, blank=True)
    phone_model = models.CharField(max_length=250, blank=True)
    android_version = models.CharField(max_length=100, blank=True)
    ram = models.CharField(max_length=250, blank=True)
    storage = models.CharField(max_length=250, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "serial_number"],
                                    name="unique mobile device")
                       ]

    def __str__(self):
        return f"{self.user.email}<{self.serial_number}>"


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
    url = models.URLField(
        max_length=500,
        default="https://netmesh-web.asti.dost.gov.ph/speedtest"
    )

    contributor = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE)

    def __str__(self):
        return "%s (%s)" % (self.nickname, self.uuid)


class MobileResult(models.Model):
    """Mobile Device Speed test result"""
    android_version = models.CharField(max_length=100, blank=True)
    ssid = models.CharField(max_length=250, blank=True)
    bssid = models.CharField(max_length=250, blank=True)
    rssi = models.FloatField(null=True, blank=True)
    network_type = models.CharField(max_length=20, blank=True)
    imei = models.CharField(max_length=250, blank=True)
    cell_id = models.CharField(max_length=250, blank=True)
    mcc = models.CharField(max_length=250, blank=True)
    mnc = models.CharField(max_length=250, blank=True)
    tac = models.CharField(max_length=250, blank=True)
    signal_quality = models.CharField(max_length=250, blank=True)
    operator = models.CharField(max_length=250, blank=True)
    lat = models.FloatField(
        default=0,
        null=True,
        blank=True,
        validators=[
            MaxValueValidator(90.0),
            MinValueValidator(-90.0)])
    lon = models.FloatField(
        default=0,
        null=True,
        blank=True,
        validators=[
            MaxValueValidator(180.0),
            MinValueValidator(-180.0)])
    upload = models.FloatField(default=0, blank=True)
    download = models.FloatField(default=0, blank=True)
    jitter = models.FloatField(default=0, null=True, blank=True)
    ping = models.FloatField(default=0, null=True, blank=True)
    timestamp = models.DateTimeField()
    success = models.BooleanField()
    server = models.ForeignKey(Server, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['timestamp', 'server'],
                name="unique mobile results")
            ]


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
    lat = models.FloatField(default=0,
                            validators=[MaxValueValidator(90.0),
                                        MinValueValidator(-90.0)])
    lon = models.FloatField(default=0,
                            validators=[MaxValueValidator(180.0),
                                        MinValueValidator(-180.0)])
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


class RfcResult(models.Model):
    """
        Model for an RFC-6349 test result
    """
    test_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        blank=True,
        unique=True
    )
    device = models.ForeignKey(RfcDevice, on_delete=models.CASCADE)
    direction = models.CharField(
        null=False,
        max_length=10,
        choices=choices.direction_choices,
        default='unknown'
    )
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    mtu = models.IntegerField(null=True, blank=True, help_text="bytes")
    baseline_rtt = models.FloatField(null=True, blank=True, help_text="ms")
    rtt = models.FloatField(null=True, blank=True, help_text="ms")
    ave_rtt = models.FloatField(null=True, blank=True)
    bb = models.FloatField(null=True, blank=True, help_text="bps")
    bdp = models.FloatField(null=True, blank=True, help_text="bits")
    rwnd = models.FloatField(null=True, blank=True, help_text="bytes")
    max_achievable_thpt = models.PositiveBigIntegerField(
        null=True, blank=True, help_text="bps")
    actual_thpt = models.PositiveBigIntegerField(
        null=True, blank=True, help_text="bps")
    ideal_transfer_time = models.FloatField(
        null=True, blank=True, help_text="s")
    acutal_transfer_time = models.FloatField(
        null=True, blank=True, help_text="s")
    transfer_time_ratio = models.FloatField(
        null=True, blank=True, help_text="unitless")
    tcp_efficiency = models.FloatField(
        null=True, blank=True, help_text="%")
    buffer_delay = models.FloatField(
        null=True, blank=True, help_text="unitless")
    tx_bytes = models.FloatField(
        null=True, blank=True)
    iperf_version = models.CharField(
        max_length=250, blank=True)
    sndbuf_actual = models.CharField(
        max_length=250, blank=True)
    rcvbuf_actual = models.CharField(
        max_length=250, blank=True)
    transfer_bytes = models.PositiveBigIntegerField(
        null=True, blank=True)
    retransmit_bytes = models.PositiveBigIntegerField(
        null=True, blank=True)
    sender_tcp_congestion = models.CharField(
        max_length=10, blank=True)
    receiver_tcp_congestion = models.CharField(
        max_length=10, blank=True)
    host_system_util = models.FloatField(
        null=True, blank=True, help_text="% utilization")
    remote_system_util = models.FloatField(
        null=True, blank=True, help_text="% utilization")
    lat = models.FloatField(
        default=0,
        validators=[
            MaxValueValidator(90.0),
            MinValueValidator(-90.0)])
    lon = models.FloatField(
        default=0,
        validators=[
            MaxValueValidator(180.0),
            MinValueValidator(-180.0)])
    location = models.CharField(max_length=250, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.direction}"


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
        default=uuid.uuid4,
        editable=False,
        blank=True,
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


class PublicSpeedTest(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    result = models.ForeignKey(MobileResult, on_delete=models.CASCADE)
    test_id = models.UUIDField(
        default=uuid.uuid4,
        null=True,
        editable=False,
        blank=True,
        unique=True
    )


class NTCSpeedTest(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    result = models.ForeignKey(MobileResult, on_delete=models.CASCADE)
    test_id = models.UUIDField(
        default=uuid.uuid4,
        null=True,
        editable=False,
        blank=True,
        unique=True
    )
    region = models.CharField(
        max_length=20, choices=choices.ntc_region_choices,
        default='unknown'
    )
    test_device = models.ForeignKey(MobileDevice,
                                    on_delete=models.CASCADE)
