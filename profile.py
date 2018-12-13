# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
import geni.rspec.igext as IG

# Create a portal context.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()


tourDescription = \
"""
This profile provides the template for a full research cluster with head node, scheduler, compute nodes, and shared file systems.
First node (head) should contain: 
- Shared home directory using Networked File System
- Management server for SLURM
Second node (metadata) should contain:
- Metadata server for SLURM
Third node (storage):
- Shared software directory (/software) using Networked File System
Remaining three nodes (computing):
- Compute nodes
"""

#
# Setup the Tour info with the above description and instructions.
#  
tour = IG.Tour()
tour.Description(IG.Tour.TEXT,tourDescription)
request.addTour(tour)


link = request.LAN("lan")

for i in range(15):
  if i == 0:
    node = request.XenVM("head")
    node.routable_control_ip = "true"
  elif i == 1:
    node = request.XenVM("metadata")
  elif i == 2:
    node = request.XenVM("storage")
  else:
    node = request.XenVM("compute-" + str(i-2))
    node.cores = 2
    node.ram = 4096
    
  node.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops:CENTOS7-64-STD"
  
  iface = node.addInterface("if" + str(i-3))
  iface.component_id = "eth1"
  iface.addAddress(pg.IPv4Address("192.168.1." + str(i + 1), "255.255.255.0"))
  link.addInterface(iface)
  
  node.addService(pg.Execute(shell="sh", command="sudo chmod 755 /local/repository/passwordless.sh"))
  node.addService(pg.Execute(shell="sh", command="sudo /local/repository/passwordless.sh"))
  
    # Ben Walker's solution to address latency
  node.addService(pg.Execute(shell="sh", command="sudo chmod 755 /local/repository/ssh_setup.sh"))
  node.addService(pg.Execute(shell="sh", command="sudo -H -u jt876084 bash -c '/local/repository/ssh_setup.sh'"))
 
  node.addService(pg.Execute(shell="sh", command="sudo su jt876084 -c 'cp /local/repository/source/* /users/jt876084'"))
  
  
  if i == 0: # head
    node.addService(pg.Execute(shell="sh", command="sudo chmod 755 /local/repository/setup_head.sh"))
    node.addService(pg.Execute(shell="sh", command="sudo /local/repository/setup_head.sh"))
    node.addService(pg.Execute(shell="sh", command="sudo chmod 755 /local/repository/install_mpi.sh"))
    node.addService(pg.Execute(shell="sh", command="sudo /local/repository/install_mpi.sh"))
    
  elif i == 2: # storage
    node.addService(pg.Execute(shell="sh", command="sudo chmod 755 /local/repository/setup_storage.sh"))
    node.addService(pg.Execute(shell="sh", command="sudo /local/repository/setup_storage.sh"))
    
  else: # compute
    node.addService(pg.Execute(shell="sh", command="sudo chmod 755 /local/repository/setup_compute.sh"))
    node.addService(pg.Execute(shell="sh", command="sudo /local/repository/setup_compute.sh"))
  
# Print the RSpec to the enclosing page.
pc.printRequestRSpec(request)
