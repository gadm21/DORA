import sys 
sys.path.append('..')


from utils import * 
from data_utils import *
from model_utils import *

from central_training import get_dataset 

central_train_set, central_test_set, public_set, local_sets, test_sets = get_dataset('depth')
central_train_dataset = HARDataset(central_train_set[0], central_train_set[1], transform = transforms.Compose([transforms.ToTensor()]))
central_test_dataset = HARDataset(central_test_set[0], central_test_set[1], transform = transforms.Compose([transforms.ToTensor()]))
central_train_dataloader = DataLoader(central_train_dataset, batch_size = 32, shuffle = True)
central_test_dataloader = DataLoader(central_test_dataset, batch_size = 32, shuffle = True)




model = HAR_CV_Net(input_shape = [20, 20], f1 = 10, f2 = 20, f3 = 25, n_classes = 5)
model2 = HAR_T_Net(n_features = 4, n_hidden = 4, n_classes = 4)
model3 = ThreeLayerMLP(4, 4)

criterion = nn.CrossEntropyLoss()
optimizer = optim.RMSprop(model.parameters(), lr=0.001)

 
EPOCHS = 10
MAX_GRAD_NORM = 1.0
EPSILON = 50.0
DELTA = 1e-5
privacy_engine = PrivacyEngine()
model, optimizer, central_train_dataloader = privacy_engine.make_private_with_epsilon(
    module=model,
    optimizer=optimizer,
    data_loader=central_train_dataloader,
    epochs=EPOCHS,
    target_epsilon=EPSILON,
    target_delta=DELTA,
    max_grad_norm=MAX_GRAD_NORM,
)

for epoch in range(EPOCHS):
    train(model, criterion, optimizer, central_train_dataloader, privacy_engine = privacy_engine, DELTA = DELTA)



test(model, central_train_dataloader, privacy_engine, DELTA)


