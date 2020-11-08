<div align="center">
	<img
		src="img/tao.png"
		alt="tao"
		width="100px"
		height="100px"
	/>
</div>

# Tao

[![Invite Tao](https://img.shields.io/badge/Invite-Tao-000000?style=flat&colorA=000000&colorB=000000)](https://discord.com/oauth2/authorize?client_id=732330652539682857&scope=bot&permissions=8)

### Usage

|                                            |                                                                                                                                  |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| **Helper functions**                       |                                                                                                                                  |
| `tao`                                      | `meta information`                                                                                                               |
| `tao info <user>`                          | `user information`                                                                                                               |
| `tao help`                                 | `command information`                                                                                                            |
|                                            |                                                                                                                                  |
| **Initialize and configure**               |                                                                                                                                  |
| `tao init [-reset]`                        | `set role and channel configuration [or reset]`                                                                                  |
| `tao config -score <-enable/-disable>`     | `enable or disable the scoring system`                                                                                           |
| `tao config -verbose <-enable/-disable>`   | `enable or disable verbose notifications`                                                                                        |
| `tao config -late <-enable/-disable>`      | `enable or disable late scoring system`                                                                                          |
| `tao config -strict <-enable/-disable>`    | `enable or disable whether to ban alt accounts`                                                                                  |
|                                            |                                                                                                                                  |
| **Bot commands**                           |                                                                                                                                  |
| `tao run -sort_user <user> `               | `manually sort user`                                                                                                             |
| `tao run -send_score_info <user> `         | `get user score`                                                                                                                 |
| `tao run -set_flag <flag> `                | `set user flag` <br>`-0 = send notification`<br>`-1 = send to manual approval`<br>`-2 = ban`<br>`-3 = valid account (no action)` |
|                                            |                                                                                                                                  |
| **Moderation commands**                    |                                                                                                                                  |
| `tao ban <user;user1;..> [-time] [reason]` | `ban user` <br>`-m = minute`<br>`-h = hour`<br>`-d = day`<br>`-w = week`                                                         |
| `tao unban <user;user1;..>`                | `unban user`                                                                                                                     |
| `tao kick <user;user1;..>`                 | `kick user`                                                                                                                      |
| `tao clear <amount>`                       | `clear messages from current channel`                                                                                            |
