from unittest import TestCase

from balancer.models import BalanceItem

from balancer.views import rand_from_balancer

class SomeTests(TestCase):

        def createItems(self, orderings, counts, group_id):

            for ordering, count in zip(orderings, counts):
                BalanceItem.objects.create(group_id=group_id, ordering=ordering, count=count)

        def updateItem(self, count, ordering, group_id):
            item = BalanceItem.objects.get(group_id=group_id, ordering=ordering)
            item.count = count
            item.save()

        def updateItems(self, counts, orderings, group_id):
            for count, ordering in zip(counts, orderings):
                self.updateItem(count, ordering, group_id)


        def test_rand_from_balancer(self):

            self.createItems("a,b,c,d".split(","), [0, 0, 0, 0], 'test')

            self.assertEqual(BalanceItem.objects.filter(group_id='test').count(), 4)

            self.updateItems([1, 1, 1], "a,b,c".split(","), 'test')

            url = rand_from_balancer('test', 0)

            self.assertEquals(url, 'd')

            self.assertEquals(BalanceItem.objects.get(group_id='test', ordering='d').count, 1)

            urls = []
            x = 4
            while x > 0:
                urls.append(rand_from_balancer('test', 0))
                x -= 1

            self.assertEquals(len(list(set(urls))), 4)

            x = 8
            while x > 0:
                rand_from_balancer('test', 0)
                x -= 1

            for item in BalanceItem.objects.filter(group_id='test'):
                self.assertEquals(item.count, 4)


