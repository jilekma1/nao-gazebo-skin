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

  //set collisions to ON
  
  


 this->InitUDP();
 std::cout << "ContactPlugin runnning.";
 std::cout << "Update rate is " << this->parentSensor->UpdateRate() << "\n";
}

/////////////////////////////////////////////////
void ContactPlugin::OnUpdate()
{
  // Get all the contacts.
  msgs::Contacts contacts;
  contacts = this->parentSensor->GetContacts();

  //common::Time time = this->parentSensor->world->GetSimTime();
  //uint32_t sensID = this->parentSensor->Id();
  //std::string = this->parentSensor->GetCollisionName(sensID);
  
  //common::Time lastUpdate = this->parentSensor->LastUpdateTime();
  //std::cout << "Last update: " << lastUpdate.FormattedString() << "\n";
  std::set<std::pair<std::string, std::string>> measuredSet;

  for (unsigned int i = 0; i < contacts.contact_size(); ++i)
  {

  std::string col1 = contacts.contact(i).collision1();
  std::string col2 = contacts.contact(i).collision2();
  std::cout << "next" << "\n";
  if(measuredSet.count(std::make_pair(col1, col2)) == 0)
  {std::cout << col1 << col2 <<"\n";
	//std::cout << "Sensor" << this->parentSensor.GetName() << "sensed collision.";

    //std::cout << "Collision between[" << contacts.contact(i).collision1()
    //          << "] and [" << contacts.contact(i).collision2() << "]\n";

	common::Time msgTime = msgs::Convert(contacts.contact(i).time());
	std::string col;

    //std::string t = contacts.contact(i).time();
    //physics::WorldPtr wp = contacts.contact(i).world;
    //const gazebo::msgs::Time msgTime = Convert(contacts.contact(i).time());
    
    
	//GET SIM TIME
    
    //std::cout << msgTime.FormattedString();

	//GET REAL TIME
	struct timespec realTime;
    clock_gettime(CLOCK_REALTIME, &realTime);
    //std::cout << realTime << "\n";
	char c[2048];
	//strcpy(c, arr.c_str());
	//strncat(strncat(c, " ", arr.length()+1), (msgTime.FormattedString()).c_str(), arr.length());

	//NAME OF THIS LINK
    std::stringstream ss;
	std::string delimiter = "::";
	std::string s = (this->parentSensor)->ParentName();
    //std::cout << "Sensor " << s << "update: " << this->parentSensor->LastUpdateTime() << "\n";
	/*
	char str[] = s.c_str();
  	char * pch;
  	printf ("Splitting string \"%s\" into tokens:\n",str);
  	pch = strtok (str," ,.-");
  	while (pch != NULL)
  	{
    	std::cout << pch;
    	pch = strtok (NULL, " ,.-");
  	}*/
	//std::cout << col1 << " " << col2 << realTime.tv_sec << "::" << realTime.tv_nsec << "\n";
	//COMPARE WITH DETECTED COLLISIONS
	if(col1.find(s))
		col = col1;
	else if(col2.find(s))
		col = col2;
	else
		std::cout << "Colliding segment not found!" << "\n";
	
	ss << col << "::" << msgTime.FormattedString() << "::" << realTime.tv_sec << "::" << realTime.tv_nsec;
	std::cout << col1 << "::" << col2 << "::" << msgTime.FormattedString() << "::" << realTime.tv_sec << "::" << realTime.tv_nsec;
    //std::cout << msgTime.FormattedString() << "\n";
	std::string ts = ss.str();
    strcpy(c, ts.c_str());


    this->SendUDP(c);
measuredSet.insert(std::make_pair(col1, col2));
    }
    else
    {
        
		//std::cout << "Discarding measurement" << "\n";
    }
	/*
    for (unsigned int j = 0; j < contacts.contact(i).position_size(); ++j)
    {
	  std::cout << col1 << "::" << msgTime.FormattedString() << "::" << realTime.tv_sec << "::" << 
	realTime.tv_nsec << "\n";
      std::cout << j << "  Position:"
                << contacts.contact(i).position(j).x() << " "
                << contacts.contact(i).position(j).y() << " "
                << contacts.contact(i).position(j).z() << "\n";
    }
	*/
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

/*
 TimeReader::TimeReader()
 {

 }

 TimeReader::~TimeReader()
 {

 }

 double TimeReader::GetSimTime(sensors::SensorPtr _sensor)
 {
	std::cout << _sensor.world->GetSimTime();
    return 0;

 }*/
