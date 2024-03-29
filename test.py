# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import subprocess
import time
import torch.optim as optim
import torch.nn.functional as F
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from IPython import get_ipython

# %% [markdown]
# # Load pytorch library

# %%
import torch
import torchvision
import torchvision.transforms as transforms

# %% [markdown]
# # Define validation dataset ratio

# %%

valid_ratio = 0.3

# %% [markdown]
# # Define the MNIST training and validation sets, and possible transforms to be applied. Optional augmentation can be done within the transform.

# %%
transform = transforms.Compose(
    [
        #  transforms.RandomRotation(degrees=30),
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))])

train_valid_dataset = torchvision.datasets.MNIST(root='./data', train=True,
                                                 download=True, transform=transform)
nb_train = int((1.0 - valid_ratio) * len(train_valid_dataset))
nb_valid = int(valid_ratio * len(train_valid_dataset))
train_dataset, valid_dataset = torch.utils.data.dataset.random_split(
    train_valid_dataset, [nb_train, nb_valid])
trainloader = torch.utils.data.DataLoader(train_dataset, batch_size=500,
                                          shuffle=True)
validloader = torch.utils.data.DataLoader(valid_dataset, batch_size=500,
                                          shuffle=True)

classes = ('0', '1', '2', '3',
           '4', '5', '6', '7', '8', '9')

# %% [markdown]
# # Visualize the MNIST dataset.

# %%

# functions to show an image


def imshow(img):
    img = img / 2 + 0.5     # unnormalize
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.show()


# get some random training images
dataiter = iter(trainloader)
images, labels = dataiter.next()

# show images
imshow(torchvision.utils.make_grid(images[:4, ]))
# print labels
print(' '.join('%5s' % classes[labels[j]] for j in range(4)))

# %% [markdown]
# # Construct the CNN.

# %%


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        """
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(32, 32, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(32 * 7 * 7, 512)
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, 10)
        """

        self.conv1 = nn.Conv2d(1, 8, 3, 1, 1)
        self.pool = nn.MaxPool2d(2, 2, 0)
        self.conv2 = nn.Conv2d(8, 16, 3, 1, 1)
        self.conv3 = nn.Conv2d(16, 16, 3, 1, 0)
        self.fc1 = nn.Linear(16 * 5 * 5, 512)
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, 10)

    def forward(self, x):
        """
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = F.relu(self.conv3(x))
        x = x.view(-1, 32 * 7 * 7)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        """

        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = F.relu(self.conv3(x))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)

        return x

# %%

# %% [markdown]
# # Instantiate the CNN and print out the number of parameters.


# %%

# %%
net = Net()
print(sum([p.numel() for p in net.parameters()]))

# %% [markdown]
# # Define the loss function and the optimizer.

# %%

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(net.parameters(), lr=0.01)

# %% [markdown]
# # Select the device to train the CNN! "cuda:0" means the first GPU device.

# %%
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)
net.to(device)

# %% [markdown]
# # Mount your google drive to current virtual machine. And define the path to store the trained CNN parameters.

# %%
#from google.colab import drive
# drive.mount('/content/drive')
PATH = 'mnist_net.pth'

# %% [markdown]
# # Train the CNN and store the best model based on the validation loss.

# %%

start_time = time.time()
best_loss = np.float('inf')
for epoch in range(10):  # loop over the dataset multiple times

    running_loss = 0.0
    for i, data in enumerate(trainloader, 0):
        # get the inputs; data is a list of [inputs, labels]
        inputs, labels = data[0].to(device), data[1].to(device)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        # print statistics
        running_loss += loss.item()
    epoch_loss = running_loss / (i+1)
    print("Epoch: ", epoch, " train loss: ", '%.3f' % epoch_loss)
    with torch.no_grad():
        running_loss = 0.0
        for i, data in enumerate(validloader, 0):
            # get the inputs; data is a list of [inputs, labels]
            inputs, labels = data[0].to(device), data[1].to(device)

            # forward
            outputs = net(inputs)
            loss = criterion(outputs, labels)

            # print statistics
            running_loss += loss.item()
        epoch_loss = running_loss / (i+1)
        print("Epoch: ", epoch, " validation loss: ", '%.3f' % epoch_loss)
        if epoch_loss < best_loss:
            torch.save(net.state_dict(), PATH)
            best_loss = epoch_loss

time_elap = (time.time() - start_time) // 60
print('Finished Training in %d mins' % time_elap)

# %% [markdown]
# # Define the test dataset.

# %%
transform = transforms.Compose(
    [transforms.ToTensor(),
     transforms.Normalize((0.1307,), (0.3081,))])
testset = torchvision.datasets.MNIST(root='./data', train=False,
                                     download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=4,
                                         shuffle=False, num_workers=1)

# %% [markdown]
# # Visualize the test dataset.

# %%


def imshow(img):
    img = img / 2 + 0.5     # unnormalize
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.show()


dataiter = iter(testloader)
images, labels = dataiter.next()

# print images
imshow(torchvision.utils.make_grid(images))
print('GroundTruth: ', ' '.join('%5s' % classes[labels[j]] for j in range(4)))

# %% [markdown]
# # Load the learned CNN parameters. This is required when you have trained the CNN and do no want to train it again by loading the learned parameters.

# %%
net.load_state_dict(torch.load(PATH))

# %% [markdown]
# # Get the predictions for the first 4 images in the test dataset.

# %%
with torch.no_grad():
    outputs = net(images.to(device))
    _, predicted = torch.max(outputs, 1)

print('Predicted: ', ' '.join('%5s' % classes[predicted[j]]
                              for j in range(4)))

# %% [markdown]
# # Infer on the whole test dataset.

# %%
testloader = torch.utils.data.DataLoader(testset, batch_size=200,
                                         shuffle=False, num_workers=1)
correct = 0
total = 0
with torch.no_grad():
    for data in testloader:
        images, labels = data
        outputs = net(images.to(device))
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels.to(device)).sum().item()

print('Accuracy of the network on the 10000 test images: %.3F %%' % (
    100 * correct / total))

# %% [markdown]
# # check the GPU device assigned by Google.

# %%
get_ipython().system('ln -sf /opt/bin/nvidia-smi /usr/bin/nvidia-smi')
print(subprocess.getoutput('nvidia-smi'))
