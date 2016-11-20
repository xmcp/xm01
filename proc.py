#coding=utf-8
import jinja2
import re
import os
import sys
import traceback
from utils import holy_open

event_names={
    'bomb power': 0,
    'bomb size': 1,
    'bomb count': 2,
    'bomb elasticity': 3,
    'bomb oblique': 4,
    'money': 10,
    'live': 11,
}
item_names={
    'bomb power': 0,
    'bomb size': 1,
    'bomb count': 2,
    'bomb elasticity': 3,
    'bomb oblique': 4,
    'special power': 10,
    'enlarge': 11,
    'speedup': 12,
    'parachute': 13,
    'bomb connect': 14,
    'teleport': 15,
}
attr_names={
    'lives': 0,
    'move speed': 1,
    'gravity': 2,
    'jump speed': 3,
    'event frequency': 4,
    'initial money': 5,
    'money growth amount': 6,
    'money growth time': 7,
    'explode time': 8,
    'revive time': 9,
    'invincible time': 10,
    'air resistance': 11,
    'death penalty': 12,
    'death reward': 13,
    'margin side': 14,
    'margin bottom': 15,
    'margin top': 16,
    'event fall speed': 17,
    'event keep time': 18,
    'bomb gravity': 19,
    'initial bomb power': 20,
    'initial bomb size': 21,
    'initial bomb count': 22,
    'initial bomb elasticity': 23,
    'initial bomb oblique': 24,
    'bomb intensity': 25,
    'minimal bomb delay': 26,
    'bomb distance zoomratio': 27,
    'bomb time zoomratio': 28,
    'bomb mass': 29,
    'engine frame delta': 50,
    'engine separate count': 51,
    'engine bomb accuracy': 52,
}


def text(x):
    return jinja2.Markup('\n'.join(['']+x))


wallx_re=re.compile(r'(?:-*\s+)?([-\d]+)\s*~\s*([-\d]+)\s+([-\d]+)(?:\s*@\s*(\d+))?$') # -- 10~20 100 @ 100
wally_re=re.compile(r'(?:\|*\s+)?([-\d]+)\s+([-\d]+)\s*~\s*([-\d]+)$') # || 100 10~20
@jinja2.contextfilter
def walls(ctx,lines):
    res=['','-1 ::walls']
    for line in filter(None,map(str.strip,lines.split('\n'))):
        matchx=wallx_re.match(line)
        if matchx:
            res.append('1 %s %s %s'%matchx.group(1,2,3))
            if matchx.group(4):
                res.append('2 %s'%matchx.group(4))
            continue
        matchy=wally_re.match(line)
        if matchy:
            res.append('0 %s %s %s'%matchy.group(2,3,1))
            continue
        raise RuntimeError(line)
    return text(res)

    
birth_re=re.compile(r'(\d+)\s+(\d+)(?:\s*@\s*(\d+))?$') # 10 10 @ 100
@jinja2.contextfilter
def birthplaces(ctx,lines):
    res=['','-1 ::birthplaces']
    for line in filter(None,map(str.strip,lines.split('\n'))):
        match=birth_re.match(line)
        if match:
            res.append('4 %s %s'%match.group(1,2))
            if match.group(3):
                res.append('5 %s'%match.group(3))
            continue
        raise RuntimeError(line)
    return text(res)
    
    
shop_re=re.compile(r'(\d+)\s+(\d+)$') # 10 10
@jinja2.contextfilter
def shops(ctx,lines):
    res=['','-1 ::shops']
    for line in filter(None,map(str.strip,lines.split('\n'))):
        match=shop_re.match(line)
        if match:
            res.append('3 %s %s'%match.group(1,2))
            continue
        raise RuntimeError(line)
    return text(res)

    
event_re=re.compile(
    r'(?P<name>[a-zA-Z0-9 ]+)'+ # event name
    r'(?:\s*.*@\s*(?P<prob>\d+).*)?'+ # @ 100
    r'(?:\s*.*\+\s*(?P<profit>\d+).*)?'+ # + 0
    r'(?:\s*.*<=\s*(?P<lv>\d+|INF|inf).*)?'+ # <= INF
    r'\s*$'
)
@jinja2.contextfilter
def events(ctx,lines):
    res=['','-1 ::events']
    for line in filter(None,map(str.strip,lines.split('\n'))):
        match=event_re.match(line)
        if match:
            event_name=match.group('name').strip()
            evt=event_names.get(event_name.lower(),event_name)
            if match.group('prob'):
                res.append('6 %s %s'%(evt,match.group('prob')))
            if match.group('profit'):
                res.append('7 %s %s'%(evt,match.group('profit')))
            if match.group('lv'):
                if match.group('lv').lower()!='inf':
                    res.append('8 %s %s'%(evt,match.group('lv')))
                else:
                    res.append('9 %s'%evt)
            continue
        raise RuntimeError(line)
    return text(res)

    
item_re=re.compile(
    r'(?P<name>[a-zA-Z0-9 ]+)\s+='+ # item name
    r'\s*(?P<msg>on|off)?\s*'+ # enabled or disabled
    r'(?:\s*(?P<cost>\d+))?'+ # = cost
    r'$'
)
@jinja2.contextfilter
def items(ctx,lines):
    res=['','-1 ::items']
    for line in filter(None,map(str.strip,lines.split('\n'))):
        match=item_re.match(line)
        if match:
            item_name=match.group('name').strip()
            itm=item_names.get(item_name.lower(),item_name)
            if match.group('msg'):
                res.append('%d %s'%(11 if match.group('msg')=='on' else 12,itm))
            if match.group('cost'):
                res.append('13 %s %s'%(itm,match.group('cost')))
            continue
        raise RuntimeError(line)
    return text(res)

    
attr_re=re.compile(r'([^=]+)\s*=\s*([\d.\-]+)')
@jinja2.contextfilter
def attributes(ctx,lines):
    res=['','-1 ::attributes']
    for line in filter(None,map(str.strip,lines.split('\n'))):
        match=attr_re.match(line)
        if match:
            attr_name=match.group(1).strip()
            atr=attr_names.get(attr_name.lower(),attr_name)
            res.append('10 %s %s'%(atr,match.group(2)))
            continue
        raise RuntimeError(line)
    return text(res)

        
env=jinja2.Environment(
    autoescape=False,
    block_start_string='{',
    block_end_string='}',
    variable_start_string='[',
    variable_end_string=']',
    comment_start_string='/*',
    comment_end_string='*/',
    line_statement_prefix='%',
    line_comment_prefix='//',
    trim_blocks=True,
    lstrip_blocks=True,
    extensions=['jinja2.ext.do'],
)
env.filters.update({
    'walls': walls,
    'birthplaces': birthplaces,
    'shops': shops,
    'events': events,
    'items': items,
    'attributes': attributes,
    'i': int,
})

multiline_re=re.compile(r'\n{3,}')
def parse(content):
    return multiline_re.sub('\n\n',env.from_string(content).render())

if __name__=='__main__':
    if len(sys.argv)>1:
        try:
            os.chdir(os.path.split(os.path.abspath(sys.argv[1]))[0])
            with holy_open(sys.argv[1],'r') as f, holy_open('out.dat','w') as fout:
                fout.write(parse(f.read()))
        except:
            traceback.print_exc()
            input('[ERROR] Press enter to quit. ')
    else:
        import traceback
        outname=input('output filename: ')
        while True:
            name=input('filename: ')
            try:
                with holy_open(name,'r') as f, holy_open(outname,'w') as fout:
                    fout.write(parse(f.read()))
            except:
                traceback.print_exc()
            else:
                print('ok')
