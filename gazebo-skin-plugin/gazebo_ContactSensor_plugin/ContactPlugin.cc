#include "ContactPlugin.hh"

using namespace gazebo;
GZ_REGISTER_SENSOR_PLUGIN(ContactPlugin)

/////////////////////////////////////////////////
ContactPlugin::ContactPlugin() : SensorPlugin()
{
}

/////////////////////////////////////////////////
ContactPlugin::~ContactPlugin()
{
  char m[] = "Shutting down...";
  SendUDP(m);
  close(this->sockd);
}

/////////////////////////////////////////////////
void ContactPlugin::Load(sensors::SensorPtr _sensor, sdf::ElementPtr /*_sdf*/)
{
  // Get the parent sensor.
  this->parentSensor =
    boost::dynamic_pointer_cast<sensors::ContactSensor>(_sensor);

  // Make sure the parent sensor is valid.
  if (!this->parentSensor)
  {
    gzerr << "ContactPlugin requires a ContactSensor.\n";
    return;
  }

  // Connect to the sensor update event.
  this->updateConnection = this->parentSensor->ConnectUpdated(
      boost::bind(&ContactPlugin::OnUpdate, this));

  // Make sure the parent sensor is active.
  this->parentSensor->SetActive(true);


 this->InitUDP();
 std::cout << "ContactPlugin runnning.";
}

/////////////////////////////////////////////////
void ContactPlugin::OnUpdate()
{
  // Get all the contacts.
  msgs::Contacts contacts;
  contacts = this->parentSensor->GetContacts();
  char arr[] = "Contact detected";
  this->SendUDP(arr);

  for (unsigned int i = 0; i < contacts.contact_size(); ++i)
  {
	//std::cout << "Sensor" << this->parentSensor.GetName() << "sensed collision.";

    std::cout << "Collision between[" << contacts.contact(i).collision1()
              << "] and [" << contacts.contact(i).collision2() << "]\n";

    for (unsigned int j = 0; j < contacts.contact(i).position_size(); ++j)
    {
      std::cout << j << "  Position:"
                << contacts.contact(i).position(j).x() << " "
                << contacts.contact(i).position(j).y() << " "
                << contacts.contact(i).position(j).z() << "\n";
      std::cout << "   Normal:"
                << contacts.contact(i).normal(j).x() << " "
                << contacts.contact(i).normal(j).y() << " "
                << contacts.contact(i).normal(j).z() << "\n";
      std::cout << "   Depth:" << contacts.contact(i).depth(j) << "\n";
    }

  }
}

  int ContactPlugin::InitUDP()
  {
    /* Create a UDP socket */
    this->sockd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockd == -1)
    {
      perror("Socket creation error");
      exit(1);
    }

    /* Configure client address */
    my_addr.sin_family = AF_INET;
    my_addr.sin_addr.s_addr = INADDR_ANY;
    my_addr.sin_port = 0;

    bind(this->sockd, (struct sockaddr*)&(this->my_addr), sizeof(this->my_addr));
    std::cout << "Socket created";

    strcpy(this->buf, "UDP status OK...");

    /* Set server address */
    this->srv_addr.sin_family = AF_INET;
    inet_aton(IP, &(this->srv_addr).sin_addr);
    this->srv_addr.sin_port = htons(atoi(PORT));

    sendto(this->sockd, this->buf, strlen(this->buf)+1, 0,
        (struct sockaddr*)&this->srv_addr, sizeof(this->srv_addr));
  }

  int ContactPlugin::SendUDP(char message[])
  {
    strcpy(this->buf, message);
    sendto(this->sockd, this->buf, strlen(this->buf)+1, 0,
        (struct sockaddr*)&this->srv_addr, sizeof(this->srv_addr));
  }
