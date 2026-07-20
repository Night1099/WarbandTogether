-- lua/main.lua -- Battle result reporter for dedicated server
-- Writes battle_result.txt when the round ends

local result_written = false

-- WSE2 Lua adds triggers to mission templates at runtime
-- Check every 5 seconds if the battle is over
game.addTrigger("mst_coop_battle", 0, 5.0, 0,
    function()
        return true  -- condition: always check
    end,
    function()
        if result_written then return end

        -- team_get_score returns the team's remaining points
        local team0_score = game.team_get_score(0)
        local team1_score = game.team_get_score(1)

        if team0_score <= 0 or team1_score <= 0 then
            local winner = 2  -- draw
            if team0_score <= 0 and team1_score > 0 then
                winner = 1  -- defender wins
            elseif team1_score <= 0 and team0_score > 0 then
                winner = 0  -- attacker wins
            end

            local f = io.open("battle_result.txt", "w")
            if f then
                f:write("winner=" .. winner .. "\n")
                f:write("attacker_casualties=0\n")
                f:write("defender_casualties=0\n")
                f:write("rounds=1\n")
                f:write("player_kills=0\n")
                f:write("player_deaths=0\n")
                f:close()
                result_written = true
                game.display_message("@Battle complete! Returning to campaign...")
            end
        end
    end
)
