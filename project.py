# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
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
# # Define the CIFAR10 training and validation sets, and possible transforms to be applied. Optional augmentation can be done within the transform.

# %%
transform = transforms.Compose(
    [transforms.ToTensor(),
     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

trainset = torchvision.datasets.CIFAR10(root='./data', train=True,
                                        download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=4,
                                          shuffle=True, num_workers=2)

classes = ('plane', 'car', 'bird', 'cat',
           'deer', 'dog', 'frog', 'horse', 'ship', 'truck')

# %% [markdown]
# # Visualize the CIFAR10 dataset.

# %%
import matplotlib.pyplot as plt
import numpy as np

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
imshow(torchvision.utils.make_grid(images))
# print labels
print(' '.join('%5s' % classes[labels[j]] for j in range(4)))

# %% [markdown]
# # Construct the CNN.

# %%
import torch.nn as nn
import torch.nn.functional as F


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# %% [markdown]
# # Instantiate the CNN and print out the number of parameters.

# %%
net = Net()
print(sum([p.numel() for p in net.parameters()]))

# %% [markdown]
# # Define a Loss function and optimizer.

# %%
import torch.optim as optim

criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

# %% [markdown]
#  # Select the device to train the CNN! "cuda:0" means the first GPU device.

# %%
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)
net.to(device)

# %% [markdown]
#  # Mount your google drive to current virtual machine. And define the path to store the trained CNN parameters.

# %%
#from google.colab import drive
# drive.mount('/content/drive')
#PATH = 'cifar10_net.pth'

# %% [markdown]
#  # Train the CNN and store the best model based on the validation loss.

# %%
for epoch in range(10):  # loop over the dataset multiple times

    running_loss = 0.0
    for i, data in enumerate(trainloader, 0):
        # get the inputs; data is a list of [inputs, labels]
        inputs, labels = data

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        # print statistics
        running_loss += loss.item()
        if i % 2000 == 1999:    # print every 2000 mini-batches
            print('[%d, %5d] loss: %.3f' %
                  (epoch + 1, i + 1, running_loss / 2000))
            running_loss = 0.0

print('Finished Training')

# %% [markdown]
# # Save the trained mode.

# %%
PATH = './cifar_net.pth'
torch.save(net.state_dict(), PATH)

# %% [markdown]
#  # Define the test dataset.

# %%
testset = torchvision.datasets.CIFAR10(root='./data', train=False,
                                       download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=4,
                                         shuffle=False, num_workers=2)

# %% [markdown]
#  # Visualize the test dataset.

# %%
dataiter = iter(testloader)
images, labels = dataiter.next()

# print images
imshow(torchvision.utils.make_grid(images))
print('GroundTruth: ', ' '.join('%5s' % classes[labels[j]] for j in range(4)))

# %% [markdown]
#  # Load the learned CNN parameters. This is required when you have trained the CNN and do no want to train it again by loading the learned parameters.

# %%
net.load_state_dict(torch.load(PATH))

# %% [markdown]
#  # Get the predictions for the first 4 images in the test dataset.

# %%
outputs = net(images)

_, predicted = torch.max(outputs, 1)

print('Predicted: ', ' '.join('%5s' % classes[predicted[j]]
                              for j in range(4)))

# %% [markdown]
#  # Infer on the whole test dataset.

# %%
correct = 0
total = 0
with torch.no_grad():
    for data in testloader:
        images, labels = data
        outputs = net(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

print('Accuracy of the network on the 10000 test images: %d %%' % (
    100 * correct / total))

# %% [markdown]
# # Get the Accuracy of each class

# %%
class_correct = list(0. for i in range(10))
class_total = list(0. for i in range(10))
with torch.no_grad():
    for data in testloader:
        images, labels = data
        outputs = net(images)
        _, predicted = torch.max(outputs, 1)
        c = (predicted == labels).squeeze()
        for i in range(4):
            label = labels[i]
            class_correct[label] += c[i].item()
            class_total[label] += 1


for i in range(10):
    print('Accuracy of %5s : %2d %%' % (
        classes[i], 100 * class_correct[i] / class_total[i]))

# %% [markdown]
#  # check the GPU device assigned by Google.

# %%
#get_ipython().system('ln -sf /opt/bin/nvidia-smi /usr/bin/nvidia-smi')
#print(subprocess.getoutput('nvidia-smi'))

