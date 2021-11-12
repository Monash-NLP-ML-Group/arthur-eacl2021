import argparse

parser = argparse.ArgumentParser()
parser.add_argument("align")
parser.add_argument("src_file")
parser.add_argument("trg_file")
parser.add_argument("--mode", choices=["align", "wait"], default="align")
parser.add_argument("--add_eos", action='store_true')
parser.add_argument("--debug", action='store_true')
parser.add_argument("--wait_num", type=int, default=1)
parser.add_argument("--add_delay", type=int, default=0)
args = parser.parse_args()

READ = "R"
WRITE = "W"


def read_data():
  """
  Reading alignment file, ex line:
  1-3 2-4 5-3
  """
  with open(args.align) as align_fp, \
       open(args.src_file) as src_fp, \
       open(args.trg_file) as trg_fp:
    for src_line, trg_line, align in zip(src_fp, trg_fp, align_fp):
      len_src = len(src_line.strip().split())
      len_trg = len(trg_line.strip().split())
      align = align.strip().split()
      align = [x.split("-") for x in align]
      align = [(int(f), int(e)) for f, e in align]
      yield len_src, len_trg, align

def split_alignment(align):
  f_to_e = {}
  e_to_f = {}
  for f, e in align:
    if f not in f_to_e: f_to_e[f] = []
    if e not in e_to_f: e_to_f[e] = []
    f_to_e[f].append(e)
    e_to_f[e].append(f)
  return f_to_e, e_to_f

#def align_missings(len_f, len_e, align):
#  f_to_e, e_to_f = split_alignment(align)
#  missing = []
#
#  for i in range(len_e-1, -1, -1):
#    if i not in e_to_f:
#      f_align = e_to_f[i+1] if i != len_e-1 else [len_f-1]
#      for f in f_align:
#        missing.append((f, i))
#      e_to_f[i] = f_align
#  return align + missing

def action_from_align(len_src, len_trg, align):
  if len_src == 0 or len_trg == 0:
    return []

  #align = align_missings(len_src, len_trg, align)
  f_to_e, e_to_f = split_alignment(align)
  actions = []

  f_cover = -1
  for j in range(len_trg):
    if j in e_to_f:
      max_f_cover = max(e_to_f[j])
      if f_cover < max_f_cover:
        actions.extend([READ] * (max_f_cover - f_cover))
        f_cover = max_f_cover
    elif j == 0:
      actions.append(READ)
      f_cover = 0
    actions.append(WRITE)
  if f_cover+1 != len_src:
    actions.extend([READ] * (len_src - f_cover - 1))
  
  assert len(actions) == (len_src + len_trg)

  if args.add_delay > 0:
    actions = [[i, a] for i, a in enumerate(actions)]
    delay = args.add_delay
    
    for i in range(len(actions)-1, -1, -1):
      if actions[i][1] == READ:
        actions[i][0] = -1
        delay -= 1
      if delay == 0:
        break

    actions = [a for i, a in sorted(actions)]

  if args.add_eos:
    last = max([i for i, x in enumerate(actions) if x == READ])
    actions.insert(last+1, READ)
    actions.append(WRITE)

  # Check before return
  return actions

def action_wait(len_src, len_trg, align):
  if args.add_eos:
    len_src += 1
    len_trg += 1
  action = []
  
  for _ in range(args.wait_num-1):
    action.append(READ)
    len_src -= 1
    if len_src == 0:
      break

  while len_src > 0 or len_trg > 0:
    if len_src > 0:
      action.append(READ)
      len_src -= 1
    if len_trg > 0:
      action.append(WRITE)
      len_trg -= 1
  return action

  
def main():
  for data in read_data():
    if args.mode == "align":
      actions = action_from_align(*data)
    elif args.mode == "wait":
      actions = action_wait(*data)
    else:
      raise ValueError()
    print(" ".join(actions))

if __name__ == '__main__':
  main()
