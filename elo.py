import turtle
import pandas as pd
import numpy as np
import random
from random import choices

# 데이터 프레임 생성

# 유저 생성 (id, name, 실제 실력 기반 고정 elo, 게임에 반영된 elo)


def create_user(create_max_user, start_elo_point):
    users = pd.DataFrame(
        {'id': [i for i in range(1, create_max_user+1)],
         'real_elo': [random.randint(1000, 1500) for i in range(1, create_max_user+1)],
         'game_elo': [start_elo_point for i in range(1, create_max_user+1)],
         'win': [0 for i in range(1, create_max_user+1)],
         'draw': [0 for i in range(1, create_max_user+1)],
         'lose': [0 for i in range(1, create_max_user+1)],
         'game_cnt': [0 for i in range(1, create_max_user+1)],
         'tier': ['bronze'for i in range(1, create_max_user+1)]
         }
    )
    return users


def get_team(users, sample_size):
    sample_users = users.sample(sample_size)
    a_team = sample_users.head(int(sample_size/2))
    b_team = sample_users.tail(int(sample_size/2))
    return a_team, b_team


def get_team_elo_point(a_team, b_team, what_elo):
    a_team_elo = a_team[what_elo].mean()
    b_team_elo = b_team[what_elo].mean()

    return a_team_elo, b_team_elo


def get_win_expectation(a_team_elo, b_team_elo):
    win_e = 1/(1+10**((b_team_elo-a_team_elo)/600))
    a_team_win_e = win_e
    b_team_win_e = 1-win_e
    return a_team_win_e, b_team_win_e


############################################ 시뮬레이션 시작 코드 ############################################

create_max_user = 2000
start_elo_point = 1200
sample_size = 10

tier = {
    "master": 0.01,
    "diamond": 0.04,
    "platinum": 0.1,
    "gold": 0.2,
    "silver": 0.3,
    "bronze": 0.35,
}


users = create_user(create_max_user, start_elo_point)


for i in range(500):

    a_team, b_team = get_team(users, sample_size)

    a_team_elo_r, b_team_elo_r = get_team_elo_point(
        a_team, b_team, what_elo='real_elo')

    a_team_elo_g, b_team_elo_g = get_team_elo_point(
        a_team, b_team, what_elo='game_elo')

    a_team_win_e_r, b_team_win_e_r = get_win_expectation(
        a_team_elo_r, b_team_elo_r)

    a_team_win_e_g, b_team_win_e_g = get_win_expectation(
        a_team_elo_g, b_team_elo_g)

    #############################################################################################################

    ### 테스트 코드###
    # print(f"A팀({a_team_elo_r}점 / 승률 : {a_team_win_e_r*100}%\n                      VS                      \nB팀({b_team_elo_r}점 / 승률 : {b_team_win_e_r*100}%")

    # 0 = 패배 / 1 = 무승부 / 2 = 승리
    # 모두 동일한 확률로 choice
    win_rst = random.choices(range(0, 3), weights=[
        a_team_win_e_r, 0, b_team_win_e_r])

    elo_k = 32
    if win_rst == [0]:  # A팀 승리
        a_team['win'] = a_team['win'] + 1
        b_team['lose'] = b_team['lose'] + 1
        # elo update
        a_team['game_elo'] = a_team['game_elo'] + elo_k * (1 - a_team_win_e_g)
        b_team['game_elo'] = b_team['game_elo'] + elo_k * (0 - b_team_win_e_g)

    elif win_rst == [1]:  # 무승부
        a_team['draw'] = a_team['draw'] + 1
        b_team['draw'] = b_team['draw'] + 1
        # elo update
        a_team['game_elo'] = a_team['game_elo'] + \
            elo_k * (0.5 - a_team_win_e_g)
        b_team['game_elo'] = b_team['game_elo'] + \
            elo_k * (0.5 - b_team_win_e_g)

    elif win_rst == [2]:  # B팀 승리
        a_team['lose'] = a_team['lose'] + 1
        b_team['win'] = b_team['win'] + 1
        # elo update
        a_team['game_elo'] = a_team['game_elo'] + elo_k * (0 - a_team_win_e_g)
        b_team['game_elo'] = b_team['game_elo'] + elo_k * (1 - b_team_win_e_g)

    teams = a_team.append(b_team)
    users_sum = pd.concat([users, teams])

    users = users_sum.drop_duplicates(subset=['id'], keep="last")

    # users = users.sort_values(by='game_elo', ascending=False,
    #                           ignore_index=True)
    users['game_cnt'] = users['win'] + users['draw'] + users['lose']

    playing_user = users[users['game_cnt'] > 0]
    playing_user = playing_user.sort_values(
        by='game_elo', ascending=False, ignore_index=True)

    playing_user_cnt = playing_user.id.count()
    bronze_cnt = int(playing_user_cnt * tier['bronze'])
    silver_cnt = int(playing_user_cnt * tier['silver'])
    gold_cnt = int(playing_user_cnt * tier['gold'])
    platinum_cnt = int(playing_user_cnt * tier['platinum'])
    diamond_cnt = int(playing_user_cnt * tier['diamond'])
    master_cnt = int(playing_user_cnt * tier['master'])

    sum_cnt = bronze_cnt + silver_cnt + gold_cnt + \
        platinum_cnt + diamond_cnt + master_cnt
    bronze_cnt = bronze_cnt + playing_user_cnt - sum_cnt

    playing_user.iloc[:master_cnt, :]['tier'] = 'master'
    playing_user.iloc[master_cnt:master_cnt +
                      diamond_cnt, :]['tier'] = 'diamond'
    playing_user.iloc[master_cnt+diamond_cnt:master_cnt +
                      diamond_cnt+platinum_cnt, :]['tier'] = 'platinum'
    playing_user.iloc[master_cnt+diamond_cnt+platinum_cnt:master_cnt +
                      diamond_cnt+platinum_cnt+gold_cnt, :]['tier'] = 'gold'
    playing_user.iloc[master_cnt+diamond_cnt+platinum_cnt+gold_cnt:master_cnt +
                      diamond_cnt+platinum_cnt+gold_cnt+silver_cnt, :]['tier'] = 'silver'
    playing_user.iloc[master_cnt+diamond_cnt+platinum_cnt+gold_cnt+silver_cnt:master_cnt +
                      diamond_cnt+platinum_cnt+gold_cnt+silver_cnt+bronze_cnt, :]['tier'] = 'bronze'

    print(i)

# to excel file.
playing_user.to_excel('users.xlsx')
