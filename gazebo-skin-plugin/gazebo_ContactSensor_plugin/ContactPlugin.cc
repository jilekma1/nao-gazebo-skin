#include "ContactPlugin.hh"
#include <memory>
#include <string>

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
    std::dynamic_pointer_cast<sensors::ContactSensor>(_sensor);

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
 std::cout << "ContactPlugin runnning." << "\n";
}

/////////////////////////////////////////////////
void ContactPlugin::OnUpdate()
{
  // Get all the contacts.
  msgs::Contacts contacts;
  contacts = this->parentSensor->Contacts();
  std::set<std::pair<std::string, std::string>> measuredSet;
  for (unsigned int i = 0; i < contacts.contact_size(); ++i)
  {

  std::string col1 = contacts.contact(i).collision1();
  std::string col2 = contacts.contact(i).collision2();

  if(measuredSet.count(std::make_pair(col1, col2)) == 0)
  {
	common::Time msgTime = msgs::Convert(contacts.contact(i).time());
	std::string col;

	//Get real time
	struct timespec realTime;
    clock_gettime(CLOCK_REALTIME, &realTime);
	char c[2048];

	//Name of parent link
    std::stringstream ss;
	std::string delimiter = "::";
	std::string s = (this->parentSensor)->ParentName();

	//Find collision name of this taxel
    col = "none";
	if(col1.find(s))
		col = col1;
	else if(col2.find(s))
		col = col2;
	else
		std::cout << "Colliding segment not found!" << "\n";
	
	ss << col << "::" << msgTime.FormattedString() << "::" << realTime.tv_sec << "::" << realTime.tv_nsec;
	//std::cout << col1 << "::" << col2 << "::" << msgTime.FormattedString() << "::" << realTime.tv_sec << "::" << realTime.tv_nsec;
	std::string ts = ss.str();
    strcpy(c, ts.c_str());

    this->SendUDP(c);
	measuredSet.insert(std::make_pair(col1, col2));
    }
  }
}

  int ContactPlugin::InitUDP()
  {
    //Create UDP socket
    this->sockd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockd == -1)
    {
      perror("Socket creation error");
      exit(1);
    }

    //Configure client address
    my_addr.sin_family = AF_INET;
    my_addr.sin_addr.s_addr = INADDR_ANY;
    my_addr.sin_port = 0;

    bind(this->sockd, (struct sockaddr*)&(this->my_addr), sizeof(this->my_addr));

    strcpy(this->buf, "UDP status OK...");

    //Set server address
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
