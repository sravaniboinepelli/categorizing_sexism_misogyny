import numpy as np   
from load_pre_proc import *
import sys
import time

conf_dict_list, conf_dict_com = load_config(sys.argv[1])
data_dict = load_data(conf_dict_com["filename"], conf_dict_com["data_folder_name"], conf_dict_com["save_folder_name"], conf_dict_com['TEST_RATIO'], conf_dict_com['VALID_RATIO'], conf_dict_com['RANDOM_STATE'], conf_dict_com['MAX_WORDS_SENT'], conf_dict_com["test_mode"], conf_dict_com["filename_map"], conf_dict_com['use_saved_data_stuff'], conf_dict_com['save_data_stuff'])

max_group_id = 2
r = 1
labs_in_all = [11,7,12,5,3,10,6,13]
# labs_in_all = []

res_path = "label_info_%s.txt" % (max_group_id+1)

def sort_by_train_coverage(trainY_list, num_labs):
	train_coverage = np.zeros(num_labs)
	for lset in trainY_list:
		for l in lset:
			train_coverage[l] += 1.0
	train_coverage /= np.sum(train_coverage)
	s_indices = np.argsort(train_coverage)
	for class_ind in s_indices:
		print("%d - %.3f" % (class_ind, train_coverage[class_ind]))		
	print("--------------")

def train_coverage(trainY_list, map_dict, num_labs):
	train_coverage = np.zeros(num_labs)
	for lset in trainY_list:
		for l in lset:
			if l in map_dict:
				train_coverage[map_dict[l]] += 1.0
	# train_coverage /= float(len(trainY_list))
	# print(train_coverage)
	train_coverage /= np.sum(train_coverage)
	# print(np.argsort(train_coverage))
	return train_coverage

def score(conf, train_c, max_group_id, out_l):
	s_arr = np.zeros(max_group_id + 1)
	# s_dict = {c:0 for c in range(max_group_id + 1)}
	for c_ind, l_id in enumerate(conf):
		for g_id in out_l[l_id]:
			s_arr[g_id] += train_c[c_ind]
	# s_arr = np.array(list(s_dict.values()))
	# s_arr_norm = s_arr/np.sum(s_arr)
	return -np.std(s_arr), s_arr

# def score(conf, train_c, max_group_id, train_labs):
# 	s_dict = {c:0 for c in range(max_group_id + 1)}
# 	mem_dict = {c:{} for c in range(max_group_id + 1)}
# 	for c_ind, g_id in enumerate(conf):
# 		s_dict[g_id] += train_c[c_ind]
# 		mem_dict[g_id][c_ind] = None
# 	s_arr = np.array(list(s_dict.values()))
# 	s_arr_norm = s_arr/np.sum(s_arr)

# 	non_emp_count_arr = np.zeros(max_group_id+1)
# 	for l_list in train_labs:
# 		for g_id in range(max_group_id + 1):
# 			for c in l_list:
# 				if c in mem_dict[g_id]:
# 					non_emp_count_arr[g_id] += 1
# 					break
# 	non_emp_count_arr_norm = non_emp_count_arr/np.sum(non_emp_count_arr)					
# 	# print(non_emp_count_arr_norm)
# 	# print(s_arr_norm)
# 	# print(np.std(non_emp_count_arr_norm))
# 	# print(np.std(s_arr_norm))
# 	s1 = -np.std(non_emp_count_arr_norm)
# 	s2 = -np.std(s_arr_norm)
# 	return (s1+s2)/2, s1, s2, non_emp_count_arr, s_arr

startTime = time.time()

def comb_rec(arr, out_a, ind, a_ind, n, r, out_l):
	if r == 0:
		# print(out_a)
		out_l.append(list(out_a))
		return
	for i in range(a_ind, n-r+1):
		out_a[ind] = arr[i]
		# t = arr[0]
		# arr[0] = arr[i]
		# arr[i] = t
		comb_rec(arr, out_a, ind+1, i+1, n, r-1, out_l)
		# t = arr[0]
		# arr[0] = arr[i]
		# arr[i] = t
	return
arr = [i for i in range(max_group_id+1)]
out_a = [0 for i in range(r)]
out_l = []	
comb_rec(arr, out_a, 0, 0, len(arr), r, out_l)
max_list_id = len(out_l)-1
print(out_l)
# exit()

rem_labs = list(set(range(data_dict['NUM_CLASSES'])) - set(labs_in_all))
map_dict = {}
for ind, l in enumerate(rem_labs):
  map_dict[l] = ind
print(map_dict)
num_labs = len(rem_labs)

train_c = train_coverage(data_dict['lab'][:data_dict['train_en_ind']], map_dict, num_labs)
print(train_c)
print("-----------")
conf = np.zeros(num_labs, dtype=np.int64)

max_sc = -np.inf
while True:
	# print(conf)
	# sc, s1, s2, non_emp_count_arr, s_arr = score(conf, train_c, max_group_id, data_dict['lab'][:data_dict['train_en_ind']])
	sc, s_arr = score(conf, train_c, max_group_id, out_l)#, data_dict['lab'][:data_dict['train_en_ind']])
	if sc > max_sc:
		max_sc = sc
		best_conf = list(conf)
		best_s_arr =s_arr
		# best_count_arr=non_emp_count_arr
	for i in range(num_labs-1, -1, -1):
		if conf[i] == max_list_id:
			conf[i] = 0
		else:
			conf[i]+= 1
			break
	if i == 0 and conf[i] == 0:
		break

with open(res_path, 'a') as f:
	sort_by_train_coverage(data_dict['lab'][:data_dict['train_en_ind']], data_dict['NUM_CLASSES'])
	# print(best_conf)
	# print(max_sc)
	# print(best_s_arr)
	# # print(best_count_arr)
	# print("-----------")
	classi_probs_label_info = [list(labs_in_all) for i in range(max_group_id+1)]
	for class_ind, l_id in enumerate(best_conf):
		for g_id in out_l[l_id]:
			classi_probs_label_info[g_id].append(rem_labs[class_ind])
	# print(classi_probs_label_info)

	classi_probs_label_str = str(classi_probs_label_info)[2:-2].replace('], [', '+').replace(', ','_')

	timeLapsed = int(time.time() - startTime + 0.5)
	hrs = timeLapsed/3600.
	t_str = "%.1f hours = %.1f minutes over %d hours\n" % (hrs, (timeLapsed % 3600)/60.0, int(hrs))

	s1 = "%s\n%s\n%s\n-----------\n%s\n%s\n%s" % (best_conf, max_sc, best_s_arr, classi_probs_label_info, classi_probs_label_str, t_str)

	print(s1)                
	f.write(s1)
