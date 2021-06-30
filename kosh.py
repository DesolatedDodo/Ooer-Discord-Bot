# Made on Asher's behalf by garlicOS®
# Adapted by DesolatedDodo on behalf of self

from discord.ext import commands
import markovify
import random
import pickle


def make_proper_sentence(model: markovify.Text) -> str:
    """ Make sentences that start with a capital letter and end with a puncutation mark. """
    puncutation = [".", "?", "!"]
    sentence = model.make_sentence().capitalize()

    if sentence[-1] not in puncutation:
        sentence += random.choice(puncutation)

    return sentence

def make_paragraph(model: markovify.Text, sentence_count_goal: int) -> str:
    """ Generate a sequence of sentences. """
    MAX_LENGTH = 2000
    essay = make_proper_sentence(model)
    addition = make_proper_sentence(model)
    sentence_count = 0

    while sentence_count < sentence_count_goal and len(essay) + len(addition) < MAX_LENGTH:
        essay += " " + addition
        addition = make_proper_sentence(model)
        sentence_count += 1

    return essay


def regenerate() -> markovify.Text:
    """ Generate the asher model from kosh-corpus.txt and cache it for next time """
    # Form a new model from the corpus file
    with open("kosh-corpus.txt") as corpus_file:
        kosh_markov = markovify.Text(corpus_file.read()).compile()
    # Pickle the new model
    with open("kosh-model.pickle", "wb+") as model_file:
        pickle.dump(kosh_markov, model_file)

    return kosh_markov


try:
    # Reconstitute the pickled model, if it exists
    with open("kosh-model.pickle", "rb") as model_file:
        print("[kosh.py] Loading kosh model from cache.")
        kosh_markov = pickle.load(model_file)
except FileNotFoundError:
    print("[kosh.py] Cached kosh model not found. Regenerating from corpus.")
    kosh_markov = regenerate()
    


class KoshCommands(commands.Cog):
    """ Commands made on Asher's behalf! (adapted by dodo) """

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def essay(self, ctx: commands.Context, sentence_count_goal=5):
        """ Generate an Kosh-esque essay. [sentences | \"max\"]"""
        await ctx.channel.trigger_typing()

        if sentence_count_goal == "max":
            sentence_count_goal = 500
        elif type(sentence_count_goal) != int:
            raise ValueError("Requested sentence count is neither a number nor \"max\"")

        await ctx.send(make_paragraph(kosh_markov, sentence_count_goal))


    @commands.command()
    async def regenerateEssayModel(self, ctx: commands.Context):
        """ Reload the corpus and make the markov model over again. """
        regenerate()



def setup(bot):
    bot.add_cog(KoshCommands(bot))
