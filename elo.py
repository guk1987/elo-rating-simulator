import pandas as pd
import numpy as np
import random


# 데이터 프레임 생성

# 유저 생성 (id, name, 실제 실력 기반 고정 elo, 게임에 반영된 elo)


def create_user(create_max_user, start_elo_point):
    users = pd.DataFrame(
        {'id': [i for i in range(1, create_max_user+1)],
         'real_elo': [random.randint(1000, 2000) for i in range(1, create_max_user+1)],
         'game_elo': [start_elo_point for i in range(1, create_max_user+1)],
         'win': [0 for i in range(1, create_max_user+1)],
         'draw': [0 for i in range(1, create_max_user+1)],
         'lose': [0 for i in range(1, create_max_user+1)]
         }
    )
    return users


def get_team(users, sample_size):
    sample_users = users.sample(sample_size)
    a_team = sample_users.head(int(sample_size/2))
    b_team = sample_users.tail(int(sample_size/2))
    return a_team, b_team


def get_team_elo_point(a_team, b_team):
    # 게임 점수로 표기되는..
    a_team_elo_g = a_team['game_elo'].mean()
    b_team_elo_g = b_team['game_elo'].mean()

    # 실제 실력(고정)
    a_team_elo_r = a_team['real_elo'].mean()
    b_team_elo_r = b_team['real_elo'].mean()

    return a_team_elo_g, b_team_elo_g, a_team_elo_r, b_team_elo_r


def get_win_expectation(a_team_elo, b_team_elo):
    win_e = 1/(1+10**((b_team_elo-a_team_elo)/600))
    a_team_win_e = win_e
    b_team_win_e = 1-win_e
    return a_team_win_e, b_team_win_e


############################################ 시뮬레이션 시작 코드 ############################################

create_max_user = 2000
start_elo_point = 1200
sample_size = 10


users = create_user(create_max_user, start_elo_point)
a_team, b_team = get_team(users, sample_size)
a_team_elo_g, b_team_elo_g, a_team_elo_r, b_team_elo_r = get_team_elo_point(
    a_team, b_team)
a_team_win_e, b_team_win_e = get_win_expectation(a_team_elo_r, b_team_elo_r)


#############################################################################################################

### 테스트 코드###
print(f"A팀({a_team_elo_r}점 / 승률 : {a_team_win_e*100}%\n                      VS                      \nB팀({b_team_elo_r}점 / 승률 : {b_team_win_e*100}%")
