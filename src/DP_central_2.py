import sys 
sys.path.append('..')


from utils import * 
from data_utils import *
from model_utils import *


EPOCHS = 10
MAX_GRAD_NORM = 1.0
EPSILON = 10.0
DELTA = 1e-5

n_pub_sets = 1
dataset = 'depth'
central_train_set, central_test_set, public_set, local_sets, test_sets = get_dataset(dataset, n_pub_sets = n_pub_sets) 
train_dl = DataLoader(HARDataset(central_train_set[0], central_train_set[1]), batch_size = 32, shuffle = False)
test_dl = DataLoader(HARDataset(central_test_set[0], central_test_set[1]), batch_size = 32, shuffle = False)
n_classes = central_train_set[1].shape[-1] # number of classes in a one-hot encoded vector

model1 = get_heterogeneous_model(0, central_train_set[0].shape, n_classes)
criterion1 = nn.CrossEntropyLoss()
optimizer1 = optim.SGD(model1.parameters(), lr=0.001)

privacy_engine = PrivacyEngine()
dpmodel, dp_opt, train_loader = privacy_engine.make_private_with_epsilon(
    module=model1,
    optimizer=optimizer1,
    data_loader=train_dl,
    epochs=EPOCHS,
    target_epsilon=EPSILON,
    target_delta=DELTA,
    max_grad_norm=MAX_GRAD_NORM,
)

for epoch in range(EPOCHS):
    
    train(dpmodel, train_loader, criterion1, dp_opt, privacy_engine, DELTA)
test(dpmodel, test_dl, criterion1, privacy_engine, DELTA)



model2 = get_heterogeneous_model(0, central_train_set[0].shape, n_classes)
criterion2 = nn.CrossEntropyLoss()
optimizer2 = optim.SGD(model2.parameters(), lr=0.001)
train_dl = DataLoader(HARDataset(central_train_set[0], central_train_set[1]), batch_size = 32, shuffle = False)
test_dl = DataLoader(HARDataset(central_test_set[0], central_test_set[1]), batch_size = 32, shuffle = False)

for epoch in range(EPOCHS):
    train(model2, train_dl, criterion2, optimizer2, privacy_engine = None, DELTA = DELTA)
test(model2, test_dl, criterion2, None, None)


# dp_attack_res = run_mia_attack(dpmodel, train_dl, test_dl) 
# nondp_attack_res = run_mia_attack(model2, train_dl, test_dl)

# f = open('dp_mia_results.txt', 'w')
# f.write(dp_attack_res.summary(by_slices=True))
# f.close()

# f = open('nondp_mia_results.txt', 'w')
# f.write(nondp_attack_res.summary(by_slices=True))
# f.close()

# print(plotting.plot_roc_curve(dp_attack_res.get_result_with_max_auc().roc_curve))
# print(plotting.plot_roc_curve(nondp_attack_res.get_result_with_max_auc().roc_curve))

